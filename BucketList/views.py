from django.shortcuts import render
from django.http import HttpResponse
from BucketList.models import BucketListItem, UserProfile, Comment
from django.contrib import auth
from forms import BucketListItemForm, UserProfileForm, UserProfileEditForm, BucketListItemEditForm, CustomItemEditForm, CommentForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from fuzzywuzzy import fuzz, process
from chartit import DataPool, Chart
import operator
from datetime import date




#-------------Functions Used Throughout Views--------------

    
def ExactSameGoal(item, dict):
        #Takes a specific BucketListItem and a Dictionary of BucketListItems and finds any exact matches on the list using FuzzyWuzzy
        list_of_goals = []
        number_of_exact = 0
        for goal in dict:
            similarity = fuzz.ratio(item, goal.text)
            if similarity == 100:
                number_of_exact += 1
                list_of_goals.append(goal)
        return list_of_goals, number_of_exact 

        
def MostSimilarGoals(item, dict):
    #Takes a specific BucketListItem and a Dictionary of BucketListItems and returns the three most similar items on the list using FuzzyWuzzy it also outputs the highest accuracy % out of of the three goals
    list_of_goals = [('item', 0), ('item', 0), ('item', 0)]
    highest_accuracy = 0
    for goal in dict:
        similarity = fuzz.token_set_ratio(item, goal.text)
        for list_item in list_of_goals:
            if similarity > list_item[1]:
                if similarity > highest_accuracy:
                    highest_accuracy = similarity
                list_of_goals.remove(list_item)
                list_of_goals.append((goal, similarity))
                break
    return list_of_goals, highest_accuracy
    
    
def RepeatGoalInList(dict):
    #Takes a Dictionary of Goals and outputs a list of any goals that are repeats
    matching_goals = []
    for item in dict:
        same_goal = ExactSameGoal(item, dict)
        if same_goal[1] > 1:
            match = same_goal[0]
            matching_goals.append(match[0])
    if len(matching_goals) > 0:
        return matching_goals[0]
    else: 
        return 0
   
   
def UsersActivity(User):
    #Takes a user argument. Assigns the user a score score based upon their activity throughout the site.  Different site actions carry separate weight and the output is a single number.
    score = 0
    
    all_list_items = BucketListItem.objects.filter(pub_by = User)
    crossed_off = BucketListItem.objects.filter(pub_by = User, crossed_off = True)
    users_comments = Comment.objects.filter(author = User)
    
    for item in all_list_items:
        comment_count = Comment.objects.filter(item = item).exclude(author = User)
        score += len(comment_count)*5
    
    score += len(all_list_items) * 1
    score += len(crossed_off) * 1
    score += len(users_comments) * 2
    
    return score 
    
    
def FindAge(born):
    #Takes a take argument and outputs the users current age based upon the age given
    today = date.today()
    try:
        birthday = born.replace(year=today.year)
    except ValueError:
        #Error raises when bday is on Feb 29 and its nor currently a leap year
        birthday = born.replace(year=today.year, month=born.month+1, day=1)
    if birthday > today:
        return today.year - born.year -1
    else:
        return today.year - born.year
    
#----------------End Functions Used Throughout Views-------------


def index(request):
    #The main Bucket List Page View, sorted by pubdate so the most recent are at the top
    
    all_list_items = BucketListItem.objects.filter(crossed_off = False).order_by('-pub_date')
    recently_crossed_off = BucketListItem.objects.filter(crossed_off = True).order_by('-pub_date')
    all_users = User.objects.all()
    
    all = BucketListItem.objects.all()
    
    users_by_activity = {}
    for user in all_users:
        users_by_activity[user] = UsersActivity(user)

    new_users_by_activity = dict(sorted(users_by_activity.iteritems(), key=operator.itemgetter(1), reverse=True)[:6])
    
            
    context = {'all_list_items': all_list_items,
                      'recently_crossed_off': recently_crossed_off,
                      'new_users_by_activity': new_users_by_activity,
    }
    
    
    return render(request, 'BucketList/index.html', context)
    
@login_required  
def index_items(request, id):
    #When a user clicks on a Bucket List Item on the index page it will take them here with a brief overview of that items information
    item = BucketListItem.objects.get(pk = id)
    current_user = UserProfile.objects.get(pk = request.user.id)
    comments = Comment.objects.filter(item = item)
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data['body']
            my_model = form.save(commit = False)
            my_model.created = timezone.now()
            my_model.author = current_user.user
            my_model.item = item
            my_model.body = body
            my_model.save()
            form = CommentForm()
    else:
        form = CommentForm()
      
            
    context = {'item': item,
                      'id': id,
                      'comments': comments,
                      'form': form,
                      'current_user': str(current_user.user),
                      }
                      

    
    return render(request, 'BucketList/index_items.html', context)
    
    
@login_required
def user_stats(request, id):
    #A public stats/profile page that displays their basic profile information as well as their bucket list
    item = User.objects.all().filter(username = id)
    item_profile = item[0].userprofile
    list_of_all = BucketListItem.objects.all().filter(pub_by = item)
    context = {'id': id,
                      'item': item[0],
                      'list_of_all': list_of_all,
                      'item_profile': item_profile,
                    }
    return render(request, 'BucketList/user_stats.html', context)
    

    
    
@login_required
def my_list(request):
    #The current users personal Bucket List view with links to create more list items or learn statistics about their list
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    repeat = RepeatGoalInList(personal_list)
    
    
    context = {'user': request.user.username,
                      'personal_list': personal_list,
                      'repeat': repeat,
                    }
                      
    return render(request, 'BucketList/mylist.html', context)
    
    
@login_required
def recommendation(request):
    #This view takes the users list items and turns it into a convenient display of the stats in a user friendly form, basically this view is the main reason everything else in this web app exists. 
    
    #---------------Important Recommendation Functions------------- 
        
    def BucketListItemListSum(list, field_to_sum):
        """Finds the total sum of cost, time, or hours"""
        sum = 0
        if field_to_sum == 'cost':
            for f in list:
                sum += float(f.cost)
        elif field_to_sum == 'time':
            for f in list:
                sum += float(f.time)     
        elif field_to_sum == 'hours':
            for f in list:
                sum += float(f.hours)   
        return sum
        
        
    def GoalDifficulty(item, wage):
        #Determines how difficult the goal is by returning the total amount of hours the goal will take.  Returns cost in hours by utilizing users hourly wage.  Returns 17 hours per day goal takes (not 24 because of time accounted for sleep and other free time
        sum = 0
        wage = float(wage)
        cost = float(item.cost)
        hours = float(item.hours)
        days = float(item.time)
        sum += days*17
        sum += (cost/wage)
        sum += hours
        return {item.text: sum}
        
        
        
    def total_amount_after_compounded(rate, yearly_earnings, years_left):
        #Enter the rate (as a decimal), yearly earnings, and yearly_left and it will output the total salary earned over that users lifetime and the salary of their final year
        total_amount_after_compounded = yearly_earnings
        annual_salary = yearly_earnings
        for f in range(0, int(years_left)):
            f = annual_salary*(1 + rate)
            annual_salary = f
            total_amount_after_compounded += f       
      
        return total_amount_after_compounded, annual_salary       

    def AverageForGoalType(type, category, all_or_user):
        #Searches through all goal using the goal type given and outputs the average cost/hours/time of that goal type takes type and category argument both as a string. For the third argument enter 1 for all users or 2 for the current user
        if all_or_user == 1:
            goals = BucketListItem.objects.filter(goal_type = type)
        elif all_or_user == 2:
            goals = BucketListItem.objects.filter(goal_type = type, pub_by = request.user)
        else:
            print "Something went wrong"
            
        sum = 0
        number_of_goals = 0
        
        if category == "cost":
            for goal in goals:
                sum += goal.cost
                number_of_goals +=1
        elif category == "hours":
            for goal in goals:
                sum += goal.hours
                number_of_goals +=1
        elif category == "time":
            for goal in goals:
                sum += goal.time
                number_of_goals +=1
        else:
            print "Something went wrong"
        
        if sum == 0 or number_of_goals == 0:
            return 0
        else:
            return sum/number_of_goals
        
    def UserHasGoalType(type):
        #Takes a goal type argument, if current user has goal with that goal type function returns True is the current user does not have a goal with that goal type the function returns False
        goals = BucketListItem.objects.filter(pub_by = request.user, goal_type = type)
        
        if len(goals) == 0:
            return False
        else:
            return True

                        
    #-----------------Passed Through to Template (simple)---------------
    
    #General Information Passed Through to Template
    user = UserProfile.objects.get(pk = request.user.id)
    
    #If profile is not filled out redirect to Profile Edit Form
    if user.age == 0 or user.life_expectancy == 0 or user.yearly_earnings == 0 or user.hourly_wage == 0:
        return HttpResponseRedirect('/bucketlist/profile/edit/')
        

        
    all_goals = BucketListItem.objects.all().filter(crossed_off = False)
    mylist = BucketListItem.objects.all().filter(pub_by = user, crossed_off = False)
    
    #If not enough Bucket List Items redirect to Create Bucket List Item Form
    if len(mylist) == 0:
        return HttpResponseRedirect('/bucketlist/create/')
        
    total_cost = BucketListItemListSum(mylist, 'cost')
    total_hours = BucketListItemListSum(mylist, 'hours')
    total_time = BucketListItemListSum(mylist, 'time')
    total_number_of_items = float(len(mylist))
    age = user.age()
    life_expectancy = float(user.life_expectancy)
    years_left = float(life_expectancy - age)
    days_left = float(years_left*365)
    yearly_earnings = float(user.yearly_earnings)
    hourly_wage = float(user.hourly_wage)
    work_hours_per_week = (yearly_earnings/hourly_wage)/52
    

    #Calculated Information Passed Through to Template
    accomplish_per_year = total_number_of_items/years_left
    days_per_goal = days_left/total_number_of_items
    cost_per_year = total_cost/years_left
    days_per_year = total_time/years_left
    hours_per_year = total_hours/years_left
    hours_per_month = hours_per_year/12
    hours_per_week = hours_per_year/52
    cost_of_average_goal = float(total_cost/total_number_of_items)
    percent_of_yearly_wage = (cost_per_year/yearly_earnings)*100

    #----------------Passed Through to Template (unique)--------------
     
    
    #Create List Of Bucket List Items from Most to Least Difficult, using GoalDifficulty Function
    dict_with_difficulty = {}
    
    for goal in mylist:
        dict_with_difficulty.update(GoalDifficulty(goal, hourly_wage))
        
    #Total Difficulty of all list items    
    total_difficulty = sum(dict_with_difficulty.values())
    average_goal_difficulty = total_difficulty/total_number_of_items
    
    #Most Difficult Goal, That Goals Difficulty, Percentage of Total Difficulty, and Number of Times Harder Than The Average Goal
    most_difficult_goal = max(dict_with_difficulty, key=dict_with_difficulty.get)
    most_difficult_goal_difficulty = dict_with_difficulty[most_difficult_goal]
    most_difficult_goal_percentage = (most_difficult_goal_difficulty/total_difficulty)*100
    most_difficult_percentage_harder = (most_difficult_goal_difficulty/average_goal_difficulty)
    years_needed_for_most_difficult = (most_difficult_goal_percentage*years_left)/100
    
    #Convert Most Difficult Goal Back Into BucketListItem
    most_difficult_bucket_list_item = BucketListItem.objects.filter(text = most_difficult_goal)
    most_difficult_bucket_list_item = most_difficult_bucket_list_item[0]
    
    #Finds Number of All Goals, Cost of all Goals, Hours of all Goals, and Time of all Goals
    total_cost_of_all_goals = 0
    total_hours_of_all_goals = 0
    total_time_of_all_goals = 0
    total_number_of_all_goals = -1
    most_difficult_more_cost_than = 0
    most_difficult_more_hours_than = 0
    most_difficult_more_days_than = 0
    
    for goals in all_goals:
        total_cost_of_all_goals += goals.cost
        total_hours_of_all_goals += goals.hours
        total_time_of_all_goals += goals.time
        total_number_of_all_goals += 1
        #Finds How Many Bucket List Items are less difficult than this one
        if goals.cost < most_difficult_bucket_list_item.cost:
            most_difficult_more_cost_than += 1
        if goals.hours < most_difficult_bucket_list_item.hours:
            most_difficult_more_hours_than += 1
        if goals.time < most_difficult_bucket_list_item.time:
            most_difficult_more_days_than += 1
    #Output Percentage of Goals the Hardest Goal is more difficult than   
    most_difficult_more_cost_than = float(most_difficult_more_cost_than)/float(total_number_of_all_goals)*100
    most_difficult_more_hours_than = float(most_difficult_more_hours_than)/float(total_number_of_all_goals)*100
    most_difficult_more_days_than = float(most_difficult_more_days_than)/float(total_number_of_all_goals)*100  
    
    #Set total_number_of_all_goals Back to Normal
    total_number_of_all_goals += 1
    
    #Finding Averages of All Goals
    average_cost_of_all_goals = total_cost_of_all_goals/total_number_of_all_goals
    
    average_hours_of_all_goals = total_hours_of_all_goals/total_number_of_all_goals
    
    average_time_of_all_goals = total_time_of_all_goals/total_number_of_all_goals
    
    
    #Percentage of cost compared to the average goal
    most_difficult_percentage_of_average_cost = float(most_difficult_bucket_list_item.cost)/float(average_cost_of_all_goals)
    
    
    #Percentage of hours compared to the average goal, average hours of all goals
    most_difficult_percentage_of_average_hours = float(most_difficult_bucket_list_item.hours)/float(average_hours_of_all_goals)
    
    average_goal_average_hours_per_year = float(average_hours_of_all_goals)/52
    
    most_difficult_average_hours_per_year = float(most_difficult_bucket_list_item.hours)/52
    
    
    #Percentage of time compared to the average goal
    most_difficult_percentage_of_average_time = float(most_difficult_bucket_list_item.time)/float(average_time_of_all_goals)
    
    most_difficult_percent_of_yearly = (most_difficult_bucket_list_item.cost/yearly_earnings)*100
    
    
    
    #Creates List Ordered From Easiest to Most Difficult
    list_with_difficulty = []
    
    #Sort Dict with Difficulty white deleting items from the list
    while len(dict_with_difficulty) > 0:
        item = max(dict_with_difficulty, key=dict_with_difficulty.get)
        list_with_difficulty.append(item)
        del dict_with_difficulty[item]
    
    
    #Sorts list_with_difficulty from above into two lists, one of the top five most difficult BucketListItems and another with the five easiest goals
    top_five_most_difficult = []
    bottom_five_least_difficult = []
    
    for item in list_with_difficulty[:5]:
        top_five_most_difficult.append(item)
        
    list_with_difficulty.reverse()
    
    for item in list_with_difficulty[:5]:
        bottom_five_least_difficult.append(item)
    
    
    #Finds Annual Salary Left After Bucket List Goals
    annual_salary_left = yearly_earnings - ((yearly_earnings*percent_of_yearly_wage)/100)
    


    

    
    
    #Salary and Total Earnings if Annual Salary Increases by 1% every year
    salary_after_compounded_1 = total_amount_after_compounded(0.01, yearly_earnings, years_left)[1]
    
    total_earnings_after_compounded_1 = total_amount_after_compounded(0.01, yearly_earnings, years_left)[0]
    
    annual_percent_after_compounded_1 = (total_cost/total_earnings_after_compounded_1)*100
    
    
    #Salary and Total Earnings if Annual Salary Increases by 2% every year
    salary_after_compounded_2 = total_amount_after_compounded(0.02, yearly_earnings, years_left)[1]
    
    total_earnings_after_compounded_2 = total_amount_after_compounded(0.02, yearly_earnings, years_left)[0]
    
    annual_percent_after_compounded_2 = (total_cost/total_earnings_after_compounded_2)*100
    
    
    #Salary and Total Earnings if Annual Salary Increases by 3% every year
    salary_after_compounded_3 = total_amount_after_compounded(0.03, yearly_earnings, years_left)[1]
    
    total_earnings_after_compounded_3 = total_amount_after_compounded(0.03, yearly_earnings, years_left)[0]
    
    annual_percent_after_compounded_3 = (total_cost/total_earnings_after_compounded_3)*100
    
    
    #Salary and Total Earnings if Annual Salary Increases by 4% every year
    salary_after_compounded_4 = total_amount_after_compounded(0.04, yearly_earnings, years_left)[1]
    
    total_earnings_after_compounded_4 = total_amount_after_compounded(0.04, yearly_earnings, years_left)[0]
    
    annual_percent_after_compounded_4 = (total_cost/total_earnings_after_compounded_4)*100
    
    
    #Salary and Total Earnings if Annual Salary Increases by 5% every year
    salary_after_compounded_5 = total_amount_after_compounded(0.05, yearly_earnings, years_left)[1]
    
    total_earnings_after_compounded_5 = total_amount_after_compounded(0.05, yearly_earnings, years_left)[0]
    
    annual_percent_after_compounded_5 = (total_cost/total_earnings_after_compounded_5)*100
        
        
       
    
    
    #Turning Data into Correct Model Format for Chartit
   
            
    #Passing Data to Chartit for Users Goal Distribution 
    ds = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.filter(pub_by = request.user).values('goal_type').annotate(how_many_items=Sum('how_many_items')),
                    },
                'terms': [
                    'goal_type',
                    'how_many_items']},
            ])
            
    UsersGoalDistributionChart = Chart(
                datasource = ds,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'how_many_items']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'Your Goal Distribution'}},)
               
               
    #Passing Data to Chartit for All Users Goal Distribution 
    ds1 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.values('goal_type').annotate(how_many_items=Sum('how_many_items')),
                    },
                'terms': [
                    'goal_type',
                    'how_many_items']},
            ])
            
    AllUsersGoalDistributionChart = Chart(
                datasource = ds1,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'how_many_items']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'All Users Goal Distribution'}},)
                        
    #Passing Data to Chartit for the Users Cost Distribution 
    
    ds2 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.filter(pub_by = request.user).values('goal_type').annotate(cost=Sum('cost')),
                    },
                'terms': [
                    'goal_type',
                    'cost',
                    ]}
            ])
        
    UsersGoalCostDistributionChart = Chart(
                datasource = ds2,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'cost']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'Your Cost Distribution By Goal Type'}},)

    #Passing Data to Chartit for the All Users Cost Distribution 
    
    ds3 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.values('goal_type').annotate(cost=Sum('cost')),
                    },
                'terms': [
                    'goal_type',
                    'cost',
                    ]}
            ])
        
    AllUsersGoalCostDistributionChart = Chart(
                datasource = ds3,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'cost']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'All Users Cost Distribution By Goal Type'}},)
                        
                       
    #Passing Data to Chartit for the Users Hours Distribution 
    
    ds4 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.filter(pub_by = request.user).values('goal_type').annotate(hours=Sum('hours')),
                    },
                'terms': [
                    'goal_type',
                    'hours',
                    ]}
            ])
        
    UsersGoalHoursDistributionChart = Chart(
                datasource = ds4,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'hours']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'Your Hours Distribution By Goal Type'}},)
              

    #Passing Data to Chartit for all Users Hours Distribution 
    
    ds5 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.values('goal_type').annotate(hours=Sum('hours')),
                    },
                'terms': [
                    'goal_type',
                    'hours',
                    ]}
            ])
        
    AllUsersGoalHoursDistributionChart = Chart(
                datasource = ds5,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'hours']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'All Users Hours Distribution By Goal Type'}},)              
        
    #Passing Data to Chartit for all Users Hours Distribution 
    
    ds6 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.filter(pub_by = request.user).values('goal_type').annotate(time=Sum('time')),
                    },
                'terms': [
                    'goal_type',
                    'time',
                    ]}
            ])
        
    UsersGoalDaysDistributionChart = Chart(
                datasource = ds6,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'time']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'Your Days Distribution By Goal Type'}},)

                        
    #Passing Data to Chartit for all Users Hours Distribution 
    
    ds7 = DataPool(
        series = 
            [{'options': {
                    'source': BucketListItem.objects.values('goal_type').annotate(time=Sum('time')),
                    },
                'terms': [
                    'goal_type',
                    'time',
                    ]}
            ])
        
    AllUsersGoalDaysDistributionChart = Chart(
                datasource = ds7,
                series_options = 
                    [{'options':{
                            'type': 'pie',
                            'stacking': False},
                        'terms': {
                            'goal_type': [
                                'time']
                            }}],
                chart_options = 
                    {'title': {
                        'text': 'All Users Days Distribution By Goal Type'}},)
                        
    #Numbers for What Else Could You Do
    
    dollar_bills_in_a_row_miles = total_cost/10320
    years_in_hotel = (total_cost/110)/365
    roses_every_week = (total_cost/75)/52
    dollar_bills_in_a_row_miles_after_tub = (total_cost - 60000)/10320
    how_many_trampolines = (total_cost-90000)/300
    number_of_friends_on_cruise = total_cost/800
    height_of_quarters_stacked = (total_cost-60000)*4*0.069/12/5280
    all_inclusive_resort = total_cost/4000
    roses_every_day = (total_cost/50)/365
    all_inclusive_resort_two_weeks = total_cost/7000
    gold_bars = total_cost/500000
    gallardos = total_cost/200000
    five_star_hotel = (total_cost/550)/365
    orcas = total_cost/1000000
    bouquet = (total_cost/220)/365
    
    
    #*******Comparing Goal Types******
    
    #Career
    user_has_goal_type_career = UserHasGoalType("Career")
    all_users_career_cost = AverageForGoalType("Career", "cost", 1)
    current_users_career_cost = AverageForGoalType("Career", "cost", 2)
    all_users_career_time = AverageForGoalType("Career", "time", 1)
    current_users_career_time = AverageForGoalType("Career", "time", 2)
    all_users_career_hours = AverageForGoalType("Career", "hours", 1)
    current_users_career_hours = AverageForGoalType("Career", "hours", 2)
    
    #Purchase
    user_has_goal_type_purchase = UserHasGoalType("Purchase")
    all_users_purchase_cost = AverageForGoalType("Purchase", "cost", 1)
    current_users_purchase_cost = AverageForGoalType("Purchase", "cost", 2)
    all_users_purchase_time = AverageForGoalType("Purchase", "time", 1)
    current_users_purchase_time = AverageForGoalType("Purchase", "time", 2)
    all_users_purchase_hours = AverageForGoalType("Purchase", "hours", 1)
    current_users_purchase_hours = AverageForGoalType("Purchase", "hours", 2)
    
    #Travel
    user_has_goal_type_travel = UserHasGoalType("Travel")
    all_users_travel_cost = AverageForGoalType("Travel", "cost", 1)
    current_users_travel_cost = AverageForGoalType("Travel", "cost", 2)
    all_users_travel_time = AverageForGoalType("Travel", "time", 1)
    current_users_travel_time = AverageForGoalType("Travel", "time", 2)
    all_users_travel_hours = AverageForGoalType("Travel", "hours", 1)
    current_users_travel_hours = AverageForGoalType("Travel", "hours", 2)
    
    #Extreme Sport
    user_has_goal_type_extreme = UserHasGoalType("Extreme Sport")
    all_users_extreme_cost = AverageForGoalType("Extreme Sport", "cost", 1)
    current_users_extreme_cost = AverageForGoalType("Extreme Sport", "cost", 2)
    all_users_extreme_time = AverageForGoalType("Extreme Sport", "time", 1)
    current_users_extreme_time = AverageForGoalType("Extreme Sport", "time", 2)
    all_users_extreme_hours = AverageForGoalType("Extreme Sport", "hours", 1)
    current_users_extreme_hours = AverageForGoalType("Extreme Sport", "hours", 2)    
    
    #Family/Social
    user_has_goal_type_family = UserHasGoalType("Family/Social")
    all_users_family_cost = AverageForGoalType("Family/Social", "cost", 1)
    current_users_family_cost = AverageForGoalType("Family/Social", "cost", 2)
    all_users_family_time = AverageForGoalType("Family/Social", "time", 1)
    current_users_family_time = AverageForGoalType("Family/Social", "time", 2)
    all_users_family_hours = AverageForGoalType("Family/Social", "hours", 1)
    current_users_family_hours = AverageForGoalType("Family/Social", "hours", 2)    
    
    #Relationship
    user_has_goal_type_relationship = UserHasGoalType("Relationship")
    all_users_relationship_cost = AverageForGoalType("Relationship", "cost", 1)
    current_users_relationship_cost = AverageForGoalType("Relationship", "cost", 2)
    all_users_relationship_time = AverageForGoalType("Relationship", "time", 1)
    current_users_relationship_time = AverageForGoalType("Relationship", "time", 2)
    all_users_relationship_hours = AverageForGoalType("Relationship", "hours", 1)
    current_users_relationship_hours = AverageForGoalType("Relationship", "hours", 2)     
    
    #Exercise/Health
    user_has_goal_type_exercise = UserHasGoalType("Exercise/Health")
    all_users_exercise_cost = AverageForGoalType("Exercise/Health", "cost", 1)
    current_users_exercise_cost = AverageForGoalType("Exercise/Health", "cost", 2)
    all_users_exercise_time = AverageForGoalType("Exercise/Health", "time", 1)
    current_users_exercise_time = AverageForGoalType("Exercise/Health", "time", 2)
    all_users_exercise_hours = AverageForGoalType("Exercise/Health", "hours", 1)
    current_users_exercise_hours = AverageForGoalType("Exercise/Health", "hours", 2)
    
    #Improving a Skill
    user_has_goal_type_skill = UserHasGoalType("Improving a Skill")
    all_users_skill_cost = AverageForGoalType("Improving a Skill", "cost", 1)
    current_users_skill_cost = AverageForGoalType("Improving a Skill", "cost", 2)
    all_users_skill_time = AverageForGoalType("Improving a Skill", "time", 1)
    current_users_skill_time = AverageForGoalType("Improving a Skill", "time", 2)
    all_users_skill_hours = AverageForGoalType("Improving a Skill", "hours", 1)
    current_users_skill_hours = AverageForGoalType("Improving a Skill", "hours", 2)
    
    #Hobby
    user_has_goal_type_hobby = UserHasGoalType("Hobby")
    all_users_hobby_cost = AverageForGoalType("Hobby", "cost", 1)
    current_users_hobby_cost = AverageForGoalType("Hobby", "cost", 2)
    all_users_hobby_time = AverageForGoalType("Hobby", "time", 1)
    current_users_hobby_time = AverageForGoalType("Hobby", "time", 2)
    all_users_hobby_hours = AverageForGoalType("Hobby", "hours", 1)
    current_users_hobby_hours = AverageForGoalType("Hobby", "hours", 2)
    
    #Building/Creating Something
    user_has_goal_type_building = UserHasGoalType("Building/Creating Something")
    all_users_building_cost = AverageForGoalType("Building/Creating Something", "cost", 1)
    current_users_building_cost = AverageForGoalType("Building/Creating Something", "cost", 2)
    all_users_building_time = AverageForGoalType("Building/Creating Something", "time", 1)
    current_users_building_time = AverageForGoalType("Building/Creating Something", "time", 2)
    all_users_building_hours = AverageForGoalType("Building/Creating Something", "hours", 1)
    current_users_building_hours = AverageForGoalType("Building/Creating Something", "hours", 2)  
    
    #Education/Self Improvement
    user_has_goal_type_education = UserHasGoalType("Education/Self Improvement")
    all_users_education_cost = AverageForGoalType("Education/Self Improvement", "cost", 1)
    current_users_education_cost = AverageForGoalType("Education/Self Improvement", "cost", 2)
    all_users_education_time = AverageForGoalType("Education/Self Improvement", "time", 1)
    current_users_education_time = AverageForGoalType("Education/Self Improvement", "time", 2)
    all_users_education_hours = AverageForGoalType("Education/Self Improvement", "hours", 1)
    current_users_education_hours = AverageForGoalType("Education/Self Improvement", "hours", 2)
    
    #Volunteering
    user_has_goal_type_volunteering = UserHasGoalType("Volunteering")
    all_users_volunteering_cost = AverageForGoalType("Volunteering", "cost", 1)
    current_users_volunteering_cost = AverageForGoalType("Volunteering", "cost", 2)
    all_users_volunteering_time = AverageForGoalType("Volunteering", "time", 1)
    current_users_volunteering_time = AverageForGoalType("Volunteering", "time", 2)
    all_users_volunteering_hours = AverageForGoalType("Volunteering", "hours", 1)
    current_users_volunteering_hours = AverageForGoalType("Volunteering", "hours", 2)
    
    
    #Your End Date
    years_left_plus_five = years_left +5
    total_cost_plus_five = total_cost/years_left_plus_five
    days_per_goal_plus_five = (years_left_plus_five*365)/total_number_of_items
    days_per_year_plus_five = total_time/years_left_plus_five
    hours_per_month_plus_five = (total_hours/years_left_plus_five)/12
    
    
    years_left_plus_ten = years_left + 10
    total_cost_plus_ten = total_cost/years_left_plus_ten
    days_per_goal_plus_ten = (years_left_plus_ten*365)/total_number_of_items
    days_per_year_plus_ten = total_time/years_left_plus_ten
    hours_per_month_plus_ten = (total_hours/years_left_plus_ten)/12
    
    years_left_plus_fifteen = years_left + 15
    total_cost_plus_fifteen = total_cost/years_left_plus_fifteen
    days_per_goal_plus_fifteen = (years_left_plus_fifteen*365)/total_number_of_items
    days_per_year_plus_fifteen = total_time/years_left_plus_fifteen
    hours_per_month_plus_fifteen = (total_hours/years_left_plus_fifteen)/12
    
    years_left_plus_twenty = years_left +20
    total_cost_plus_twenty = total_cost/years_left_plus_twenty
    days_per_goal_plus_twenty = (years_left_plus_twenty*365)/total_number_of_items
    days_per_year_plus_twenty = total_time/years_left_plus_twenty
    hours_per_month_plus_twenty = (total_hours/years_left_plus_twenty)/12
    
    years_left_minus_five = years_left - 5
    total_cost_minus_five = total_cost/years_left_minus_five
    days_per_goal_minus_five = (years_left_minus_five*365)/total_number_of_items
    days_per_year_minus_five = total_time/years_left_minus_five
    hours_per_month_minus_five = (total_hours/years_left_minus_five)/12
    
    years_left_minus_ten = years_left - 10
    total_cost_minus_ten = total_cost/years_left_minus_ten
    days_per_goal_minus_ten = (years_left_minus_ten*365)/total_number_of_items
    days_per_year_minus_ten = total_time/years_left_minus_ten
    hours_per_month_minus_ten = (total_hours/years_left_minus_ten)/12
    
    years_left_minus_fifteen = years_left - 15
    total_cost_minus_fifteen = total_cost/years_left_minus_fifteen
    days_per_goal_minus_fifteen = (years_left_minus_fifteen*365)/total_number_of_items
    days_per_year_minus_fifteen = total_time/years_left_minus_fifteen
    hours_per_month_minus_fifteen = (total_hours/years_left_minus_fifteen)/12
    
    years_left_minus_twenty = years_left - 20
    total_cost_minus_twenty = total_cost/years_left_minus_twenty
    days_per_goal_minus_twenty = (years_left_minus_twenty*365)/total_number_of_items
    days_per_year_minus_twenty = total_time/years_left_minus_twenty
    hours_per_month_minus_twenty = (total_hours/years_left_minus_twenty)/12
    
    #--------------------Passed To Template-----------------------              
    
    context = {
                     #-------Top Stats & Basic Overview------
                     'user': user,
                     'mylist': mylist,
                     'total_cost': total_cost,
                     'total_hours': total_hours,
                     'total_time': total_time,
                     'total_number_of_items': total_number_of_items,
                     'age': age,
                     'life_expectancy': life_expectancy,
                     'years_left': years_left,
                     'yearly_earnings': yearly_earnings,
                     'hourly_wage': hourly_wage,
                     'work_hours_per_week': work_hours_per_week,
                     
                     'accomplish_per_year': accomplish_per_year,
                     'days_per_goal': days_per_goal,
                     'cost_per_year': cost_per_year,
                     'days_per_year': days_per_year,
                     'hours_per_year': hours_per_year,
                     'hours_per_month': hours_per_month,
                     'hours_per_week': hours_per_week,
                     'cost_of_average_goal': cost_of_average_goal,
                     'percent_of_yearly_wage': percent_of_yearly_wage,
                     
                     #--------------Most Difficult Goal--------------
                     'total_difficulty': total_difficulty,
                     'years_needed_for_most_difficult': years_needed_for_most_difficult,
                     'most_difficult_goal': most_difficult_goal,
                     'most_difficult_bucket_list_item': most_difficult_bucket_list_item,
                     'most_difficult_goal_percentage':most_difficult_goal_percentage,
                     'most_difficult_percentage_harder': most_difficult_percentage_harder,
                     'total_number_of_all_goals': total_number_of_all_goals,
                     'most_difficult_more_cost_than': most_difficult_more_cost_than,
                     'most_difficult_more_hours_than':
                     most_difficult_more_hours_than,
                     'most_difficult_more_days_than': most_difficult_more_days_than,
                     'average_cost_of_all_goals': average_cost_of_all_goals,
                     'average_time_of_all_goals': average_time_of_all_goals,
                     'average_hours_of_all_goals': average_hours_of_all_goals,
                     'most_difficult_percentage_of_average_cost': most_difficult_percentage_of_average_cost,
                     'most_difficult_percentage_of_average_hours':
                     most_difficult_percentage_of_average_hours,
                     'most_difficult_percentage_of_average_time':
                     most_difficult_percentage_of_average_time,
                     'average_goal_average_hours_per_year':
                     average_goal_average_hours_per_year,
                     'most_difficult_average_hours_per_year':
                     most_difficult_average_hours_per_year,
                     'most_difficult_percent_of_yearly':
                     most_difficult_percent_of_yearly,
                     
                     
                     #---------------Top 5 Top & Bottom-------------
                     'list_with_difficulty': list_with_difficulty,
                     'top_five_most_difficult': top_five_most_difficult,                    
                     'bottom_five_least_difficult': bottom_five_least_difficult,
                     
                     #---------Analysing Your Yearly Income---------
                     'annual_salary_left': annual_salary_left,
                     'salary_after_compounded_1': salary_after_compounded_1,
                     'annual_percent_after_compounded_1':
                     annual_percent_after_compounded_1,
                     'salary_after_compounded_2':  salary_after_compounded_2,
                     'annual_percent_after_compounded_2': annual_percent_after_compounded_2,
                     'salary_after_compounded_3': salary_after_compounded_3,
                     'annual_percent_after_compounded_3': annual_percent_after_compounded_3,
                     'salary_after_compounded_4': salary_after_compounded_4,
                     'annual_percent_after_compounded_4': annual_percent_after_compounded_4,
                     'salary_after_compounded_5': salary_after_compounded_5,
                     'annual_percent_after_compounded_5': annual_percent_after_compounded_5,
                     
                     #----------------Distribution of Goals-------------

                     'charts': [UsersGoalDistributionChart, AllUsersGoalDistributionChart, UsersGoalCostDistributionChart, AllUsersGoalCostDistributionChart, UsersGoalHoursDistributionChart, AllUsersGoalHoursDistributionChart, UsersGoalDaysDistributionChart, AllUsersGoalDaysDistributionChart],
                        
                     

                      #----------------What Else Could You Do?----------
                      'dollar_bills_in_a_row_miles': dollar_bills_in_a_row_miles,
                      'years_in_hotel': years_in_hotel,
                      'roses_every_week': roses_every_week,
                      'dollar_bills_in_a_row_miles_after_tub': dollar_bills_in_a_row_miles_after_tub,
                      'how_many_trampolines': how_many_trampolines,
                      'number_of_friends_on_cruise': number_of_friends_on_cruise,
                      'height_of_quarters_stacked': height_of_quarters_stacked,
                      'all_inclusive_resort': all_inclusive_resort,
                      'roses_every_day': roses_every_day,
                      'all_inclusive_resort_two_weeks': all_inclusive_resort_two_weeks,
                      'gold_bars': gold_bars,
                      'gallardos': gallardos,
                      'five_star_hotel': five_star_hotel,
                      'orcas': orcas,
                      'bouquet': bouquet,
                      
                      
                      #--------------Comparing Goal Types--------------
                      'user_has_goal_type_career': user_has_goal_type_career,
                      'all_users_career_cost': all_users_career_cost,
                      'current_users_career_cost': current_users_career_cost,
                      'all_users_career_time': all_users_career_time,
                      'current_users_career_time': current_users_career_time,
                      'all_users_career_hours': all_users_career_hours,
                      'current_users_career_hours': current_users_career_hours,
                     
                     'user_has_goal_type_purchase': user_has_goal_type_purchase,
                     'all_users_purchase_cost': all_users_purchase_cost,
                     'current_users_purchase_cost': current_users_purchase_cost,
                     'all_users_purchase_time': all_users_purchase_time,
                     'current_users_purchase_time': current_users_purchase_time,
                     'all_users_purchase_hours': all_users_purchase_hours,
                     'current_users_purchase_hours': current_users_purchase_hours,
                     
                     'user_has_goal_type_travel': user_has_goal_type_travel,
                     'all_users_travel_cost': all_users_travel_cost,
                     'current_users_travel_cost': current_users_travel_cost,
                     'all_users_travel_time': all_users_travel_time,
                     'current_users_travel_time': current_users_travel_time,
                     'all_users_travel_hours': all_users_travel_hours,
                     'current_users_travel_hours': current_users_travel_hours,
                     
                     'user_has_goal_type_extreme': user_has_goal_type_extreme,
                     'all_users_extreme_cost': all_users_extreme_cost,
                     'current_users_extreme_cost': current_users_extreme_cost,
                     'all_users_extreme_time': all_users_extreme_time,
                     'current_users_extreme_time': current_users_extreme_time,
                     'all_users_extreme_hours': all_users_extreme_hours,
                     'current_users_extreme_hours': current_users_extreme_hours,
                     
                     'user_has_goal_type_family': user_has_goal_type_family,
                     'all_users_family_cost': all_users_family_cost,
                     'current_users_family_cost': current_users_family_cost,
                     'all_users_family_time': all_users_family_time,
                     'current_users_family_time': current_users_family_time,
                     'all_users_family_hours': all_users_family_hours,
                     'current_users_family_hours': current_users_family_hours,
                     
                     'user_has_goal_type_relationship': user_has_goal_type_relationship,
                     'all_users_relationship_cost': all_users_relationship_cost,
                     'current_users_relationship_cost': current_users_relationship_cost,
                     'all_users_relationship_time': all_users_relationship_time,
                     'current_users_relationship_time': current_users_relationship_time,
                     'all_users_relationship_hours': all_users_relationship_hours,
                     'current_users_relationship_hours': current_users_relationship_hours,
                     
                     'user_has_goal_type_exercise': user_has_goal_type_exercise,
                     'all_users_exercise_cost': all_users_exercise_cost,
                     'current_users_exercise_cost': current_users_exercise_cost,
                     'all_users_exercise_time': all_users_exercise_time,
                     'current_users_exercise_time': current_users_exercise_time,
                     'all_users_exercise_hours': all_users_exercise_hours,
                     'current_users_exercise_hours': current_users_exercise_hours,
                     
                     'user_has_goal_type_skill': user_has_goal_type_skill,
                     'all_users_skill_cost': all_users_skill_cost,
                     'current_users_skill_cost': current_users_skill_cost,
                     'all_users_skill_time': all_users_skill_time,
                     'current_users_skill_time': current_users_skill_time,
                     'all_users_skill_hours': all_users_skill_hours,
                     'current_users_skill_hours': current_users_skill_hours,
                     
                     'user_has_goal_type_hobby': user_has_goal_type_hobby,
                     'all_users_hobby_cost': all_users_hobby_cost,
                     'current_users_hobby_cost': current_users_hobby_cost,
                     'all_users_hobby_time': all_users_hobby_time,
                     'current_users_hobby_time': current_users_hobby_time,
                     'all_users_hobby_hours': all_users_hobby_hours,
                     'current_users_hobby_hours': current_users_hobby_hours,
                     
                     'user_has_goal_type_building': user_has_goal_type_building,
                     'all_users_building_cost': all_users_building_cost,
                     'current_users_building_cost': current_users_building_cost,
                     'all_users_building_time': all_users_building_time,
                     'current_users_building_time': current_users_building_time,
                     'all_users_building_hours': all_users_building_hours,
                     'current_users_building_hours': current_users_building_hours,
                     
                     'user_has_goal_type_education': user_has_goal_type_education,
                     'all_users_education_cost': all_users_education_cost,
                     'current_users_education_cost': current_users_education_cost,
                     'all_users_education_time': all_users_education_time,
                     'current_users_education_time': current_users_education_time,
                     'all_users_education_hours': all_users_education_hours,
                     'current_users_education_hours': current_users_education_hours,
                     
                     'user_has_goal_type_volunteering': user_has_goal_type_volunteering,
                     'all_users_volunteering_cost': all_users_volunteering_cost,
                     'current_users_volunteering_cost': current_users_volunteering_cost,
                     'all_users_volunteering_time': all_users_volunteering_time,
                     'current_users_volunteering_time': current_users_volunteering_time,
                     'all_users_volunteering_hours': all_users_volunteering_hours,
                     'current_users_volunteering_hours': current_users_volunteering_hours,
                     
                     #----------------Your End Date------------------
                    'years_left_plus_five': years_left_plus_five,
                    'total_cost_plus_five': total_cost_plus_five,
                    'days_per_goal_plus_five': days_per_goal_plus_five,
                    'days_per_year_plus_five': days_per_year_plus_five,
                    'hours_per_month_plus_five': hours_per_month_plus_five,
                    
                    'years_left_plus_ten': years_left_plus_ten,
                    'total_cost_plus_ten': total_cost_plus_ten,
                    'days_per_goal_plus_ten': days_per_goal_plus_ten,
                    'days_per_year_plus_ten': days_per_year_plus_ten,
                    'hours_per_month_plus_ten': hours_per_month_plus_ten,
                    
                    'years_left_plus_fifteen': years_left_plus_fifteen,
                    'total_cost_plus_fifteen': total_cost_plus_fifteen,
                    'days_per_goal_plus_fifteen': days_per_goal_plus_fifteen,
                    'days_per_year_plus_fifteen': days_per_year_plus_fifteen,
                    'hours_per_month_plus_fifteen': hours_per_month_plus_fifteen,
                    
                    'years_left_plus_twenty': years_left_plus_twenty,
                    'total_cost_plus_twenty': total_cost_plus_twenty,
                    'days_per_goal_plus_twenty': days_per_goal_plus_twenty,
                    'days_per_year_plus_twenty': days_per_year_plus_twenty,
                    'hours_per_month_plus_twenty': hours_per_month_plus_twenty,
                    
                    'years_left_minus_five': years_left_minus_five,
                    'total_cost_minus_five': total_cost_minus_five,
                    'days_per_goal_minus_five': days_per_goal_minus_five,
                    'days_per_year_minus_five': days_per_year_minus_five,
                    'hours_per_month_minus_five': hours_per_month_minus_five,
                    
                    'years_left_minus_ten': years_left_minus_ten,
                    'total_cost_minus_ten': total_cost_minus_ten,
                    'days_per_goal_minus_ten': days_per_goal_minus_ten,
                    'days_per_year_minus_ten': days_per_year_minus_ten,
                    'hours_per_month_minus_ten': hours_per_month_minus_ten,
                    
                    'years_left_minus_fifteen': years_left_minus_fifteen,
                    'total_cost_minus_fifteen': total_cost_minus_fifteen,
                    'days_per_goal_minus_fifteen': days_per_goal_minus_fifteen,
                    'days_per_year_minus_fifteen': days_per_year_minus_fifteen,
                    'hours_per_month_minus_fifteen': hours_per_month_minus_fifteen,
                    
                    'years_left_minus_twenty': years_left_minus_twenty,
                    'total_cost_minus_twenty': total_cost_minus_twenty,
                    'days_per_goal_minus_twenty': days_per_goal_minus_twenty,
                    'days_per_year_minus_twenty': days_per_year_minus_twenty,
                    'hours_per_month_minus_twenty': hours_per_month_minus_twenty,
                    
                   }

    return render(request, 'BucketList/recommendation.html', context)
    
   
    
    
@login_required
def view_my_list_item(request, id):
    #View of a current users Bucket List Item with options to cross off or edit the Bucket List Item

    item = BucketListItem.objects.get(pk = id)

    if item.pub_by != request.user:
        return HttpResponseRedirect('/accounts/login/')
        
    context = {'item': item,
                    }
                    
    return render(request, 'BucketList/view_my_list_item.html', context)
    
    
    
@login_required
def cross_off_my_list_item(request, id):
    #The view that crosses off the Bucket List Item
    item = BucketListItem.objects.get(pk = id)
    
    if item.pub_by != request.user:
        return HttpResponseRedirect('/accounts/login/')
        
    item.crossed_off = True
    item.pub_date = timezone.now()
    item.save()
    
    context = {'item': item,
                      'User': User,
                    }
                    
    return render(request, 'BucketList/crossed_off.html', context)
    
    
    
@login_required
def uncross_my_list_item(request, id):
    #The view that uncrosses off the Bucket List Item
    item = BucketListItem.objects.get(pk = id)
    
    if item.pub_by != request.user:
        return HttpResponseRedirect('/accounts/login/')
        
    item.crossed_off = False
    item.pub_date = timezone.now()
    item.save()
    
    context = {'item': item,
                      'User': User,
                    }
    return render(request, 'BucketList/uncross.html', context)
    
    
 
@login_required
def delete_my_list_item(request, id):
    #The view that uncrosses off the Bucket List Item
    item = BucketListItem.objects.get(pk = id)
    
    if item.pub_by != request.user:
        return HttpResponseRedirect('/accounts/login/')
        
    title = item.text
    item.delete()
    
    context = {'title': title,
                      'User': User,
                    }
                    
    return render(request, 'BucketList/delete.html', context)
    
    
    
@login_required
def create(request):
    #Creates a Bucket List Item, the user only fills out the Name and Type of the item while the rest of the fields are auto-filled: publication date, published by, crossed off, time, hours, and cost 
    if request.POST:
        form = BucketListItemForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            my_model = form.save(commit = False)
            new_cost = form.cleaned_data['cost']
            new_time = form.cleaned_data['time']
            new_hours = form.cleaned_data['hours']
            my_model.pub_by = user
            my_model.crossed_off = False
            my_model.time = new_time
            my_model.hours = new_hours
            my_model.cost = new_cost
            my_model.save()
            return HttpResponseRedirect('/bucketlist/mylist/compare/%s' % my_model.id)
    else:
        form = BucketListItemForm()
            
    args = {}

    args['form'] = form
        
    return render(request, 'BucketList/create_item.html', args)
        
                
@login_required
def edit_bucket_list_item(request, id):
    #This view lets the user edit their Bucket List Item and directs them to other forms necessary to make the changes needed  
    
   
    user = UserProfile.objects.get(pk = request.user.id)
    all_goals_not_users = BucketListItem.objects.all().exclude(pub_by = user)    
    
    item = BucketListItem.objects.get(pk = id)
    
    if item.pub_by != request.user:
        return HttpResponseRedirect('/accounts/login/')
     
    if request.method == "POST":
        form = BucketListItemEditForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            goal_type = form.cleaned_data['goal_type']
            cost = form.cleaned_data['cost']
            time = form.cleaned_data['time']
            hours = form.cleaned_data['hours']
            item.text = text
            item.cost = cost
            item.time = time
            item.hours = hours
            item.goal_type = goal_type
            item.pub_date = timezone.now()
            item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
    else:
        form = BucketListItemEditForm({'text': item.text, 'goal_type': item.goal_type, 'cost': item.cost, 'time': item.time, 'hours': item.hours})
        exact_same = ExactSameGoal(item.text, all_goals_not_users)
        most_similar = MostSimilarGoals(item.text, all_goals_not_users)
        most_similar_accuracy = most_similar[1]
        most_similar = most_similar[0]
        exact_same_list = exact_same[0]
        exact_same_num = exact_same[1]
        
        context = {'form': form,
                           'id': item.id,
                           'exact_same_list': exact_same_list,
                           'exact_same_num': exact_same_num,
                           'most_similar': most_similar,
                           'most_similar_accuracy': most_similar_accuracy,
                          }

        
    return render(request, 'BucketList/edit_bucket_list_item.html', context)

  
@login_required
def edit_profile(request):
    #A view that allows the user to edit their current profile information
    current_user = UserProfile.objects.get(pk = request.user.id)
    if request.method == "POST":
        form = UserProfileEditForm(request.POST)
        if form.is_valid():
            #new_age = form.cleaned_data['new_age']
            new_life_expectancy = form.cleaned_data['new_life_expectancy']
            new_yearly_earnings = form.cleaned_data['new_yearly_earnings']
            new_hourly_wage = form.cleaned_data['new_hourly_wage']
            new_birth_date = form.cleaned_data['new_birth_date']
            current_user.yearly_earnings = new_yearly_earnings
            current_user.hourly_wage = new_hourly_wage
            current_user.life_expectancy = new_life_expectancy
            #current_user.age = FindAge(new_birth_date) 
            current_user.birth_date = new_birth_date
            current_user.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
        else:
            form = UserProfileEditForm({'new_birth_date': current_user.birth_date, 'new_life_expectancy': current_user.life_expectancy, 'new_yearly_earnings': current_user.yearly_earnings, 'new_hourly_wage': current_user.hourly_wage})
            
            context = {'form': form,}
    else:
        form = UserProfileEditForm({'new_birth_date': current_user.birth_date, 'new_life_expectancy': current_user.life_expectancy, 'new_yearly_earnings': current_user.yearly_earnings, 'new_hourly_wage': current_user.hourly_wage})
        
        context = {'form': form,
                        }

    return render(request, 'BucketList/edit_user_profile.html', context)
    
    
@login_required
def compare_my_list_item(request, id):
    #View received after new item creation, shows user other similar goals to their own.  Gives user option to redirect to edit form. 
    user = UserProfile.objects.get(pk = request.user.id)
    all_goals_not_users = BucketListItem.objects.all().exclude(pub_by = user)
    item = BucketListItem.objects.get(pk = id)
    
    exact_same = ExactSameGoal(item.text, all_goals_not_users)
    most_similar = MostSimilarGoals(item.text, all_goals_not_users)
    most_similar_accuracy = most_similar[1]
    most_similar = most_similar[0]
    exact_same_list = exact_same[0]
    exact_same_num = exact_same[1]
    
    context = {'item': item,
                      'most_similar': most_similar,
                      'most_similar_accuracy': most_similar_accuracy,
                      'exact_same_list': exact_same_list,
                      'exact_same_num': exact_same_num,
    }
    
    return render(request, 'BucketList/my_list_compare.html', context)
    
        
@login_required
def delete_comment(request, id):

    comment = Comment.objects.get(pk = id)
    is_comment = 0
    item_id = comment.item.id
    
    if comment:
        is_comment = 1
        comment.delete()
        
    context = {'is_comment': is_comment,
                      'item_id': item_id,
    }
    
    return render(request, 'BucketList/delete_comment.html', context)