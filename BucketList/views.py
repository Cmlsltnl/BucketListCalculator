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



def index(request):
    #The main Bucket List Page View, sorted by pubdate so the most recent are at the top
    all_list_items = BucketListItem.objects.all().order_by('-pub_date')
    
    context = {'all_list_items': all_list_items}
    
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
def index_stats(request):
    #This page compiles interesting statistics about all of the Bucket List Items on the main index page and displays that information
    list_of_all = BucketListItem.objects.all().count()
    total_cost = BucketListItem.objects.all().aggregate(Sum('cost'))
    total_time = BucketListItem.objects.all().aggregate(Sum('time'))
    total_crossed_off = BucketListItem.objects.all().aggregate(Sum('crossed_off'))
    number_of_users = User.objects.all().count()
    cost_per_user = total_cost['cost__sum']/number_of_users
    time_per_user = total_time['time__sum']/number_of_users
    items_per_user = list_of_all/number_of_users
    crossed_off_per_user = total_crossed_off['crossed_off__sum']/number_of_users
    
    context = {'list_of_all': list_of_all,
                      'total_cost': total_cost['cost__sum'],
                      'total_time': total_time['time__sum'],
                      'total_crossed_off': total_crossed_off['crossed_off__sum'],
                      'crossed_off_per_user': crossed_off_per_user,
                      'number_of_users': number_of_users,
                      'cost_per_user': cost_per_user,
                      'time_per_user': time_per_user,
                      'items_per_user': items_per_user,
                      }
                      
    return render(request, 'BucketList/index_stats.html', context)
    
    
@login_required
def my_list(request):
    #The current users personal Bucket List view with links to create more list items or learn statistics about their list
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    
    context = {'personal_list': personal_list,
                      'user': request.user.username
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
        
        
    def GoalTypePercentages(list):
        #Figures out the distribution of different goal types and returns the percentage amount of each goal category
        travel = 0
        purchase = 0
        career = 0
        extreme = 0
        family = 0
        relationship = 0
        health = 0
        skill = 0
        hobby = 0
        building = 0
        education = 0
        volunteering = 0
        other = 0
        sum_of_all = 0
        for goal in list:
            sum_of_all += 1
            if goal.goal_type == 'Travel':
                travel += 1
            elif goal.goal_type == 'Purchase':
                purchase += 1
            elif goal.goal_type == 'Career':
                career += 1
            elif goal.goal_type == 'Extreme Sport':
                extreme += 1
            elif goal.goal_type == 'Family/Social':
                family += 1
            elif goal.goal_type == 'Relationship':
                relationship += 1
            elif goal.goal_type == 'Exercise/Health':
                health += 1
            elif goal.goal_type == 'Improving a Skill':
                skill += 1
            elif goal.goal_type == 'Hobby':
                hobby += 1
            elif goal.goal_type == 'Building/Creating Somthing':
                building += 1
            elif goal.goal_type == 'Education/Self Improvement':
                education += 1
            elif goal.goal_type == 'Volunteering':
                volunteering += 1
            elif goal.goal_type == 'Other':
                other +=1
            else:
                print "Houston we've got a problem"
        totals ={}
        totals['Travel'] = float(travel)/float(sum_of_all)*100
        totals['Purchases'] = float(purchase)/float(sum_of_all)*100
        totals['Career'] = float(career)/float(sum_of_all)*100
        totals['Extreme Sports'] = float(extreme)/float(sum_of_all)*100
        totals['Family/Social'] = float(family)/float(sum_of_all)*100
        totals['Relationships'] = float(relationship)/float(sum_of_all)*100
        totals['Exercise/Health'] = float(health)/float(sum_of_all)*100
        totals['Improving Skills'] = float(skill)/float(sum_of_all)*100
        totals['Hobbys'] = float(hobby)/float(sum_of_all)*100
        totals['Building/Creating Somthing'] = float(building)/float(sum_of_all)*100
        totals['Education/Self Improvement'] = float(education)/float(sum_of_all)*100
        totals['Volunteering'] = float(volunteering)/float(sum_of_all)*100
        totals['Other'] = float(other)/float(sum_of_all)*100
        highest = 0
        highest_total = 0
        for f in totals:
            if totals[f] > highest_total:
                highest = f
                highest_total = totals[f] 
                
        highest = (highest, highest_total)   
        return totals, highest    
    
        
    def total_amount_after_compounded(rate, yearly_earnings, years_left):
        #Enter the rate (as a decimal), yearly earnings, and yearly_left and it will output the total salary earned over that users lifetime and the salary of their final year
        total_amount_after_compounded = yearly_earnings
        annual_salary = yearly_earnings
        for f in range(0, int(years_left)):
            f = annual_salary*(1 + rate)
            annual_salary = f
            total_amount_after_compounded += f       
      
        return total_amount_after_compounded, annual_salary       

        
        
    def MoreGoalTypePercentages(list, type):
        #Figures out what percentage of cost, hours, or time each goal makes up out of the total cost, hours, or time for users list.  Enter 1 for cost, 2 for hours, or 3 for time.         
        
            
        travel = 0
        purchase = 0
        career = 0
        extreme = 0
        family = 0
        relationship = 0
        health = 0
        skill = 0
        hobby = 0
        building = 0
        education = 0
        volunteering = 0
        other = 0
        sum_of_all = 0
        
        for goal in list:
            if type == 1:
                goal_value = goal.cost
            elif type == 2:
                goal_value = goal.hours
            elif type == 3:
                goal_value = goal.time
            else:
                print "You fucked up... Woops!"
                
            sum_of_all += goal_value
            
            if goal.goal_type == 'Travel':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                travel += goal_value
                
            elif goal.goal_type == 'Purchase':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                purchase += goal_value
                
            elif goal.goal_type == 'Career':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                career += goal_value
                
            elif goal.goal_type == 'Extreme Sport':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                extreme += goal_value
                
            elif goal.goal_type == 'Family/Social':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                family += goal_value
                
            elif goal.goal_type == 'Relationship':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                relationship += goal_value
                
            elif goal.goal_type == 'Exercise/Health':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                health += goal_value
                
            elif goal.goal_type == 'Improving a Skill':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                skill += goal_value
                
            elif goal.goal_type == 'Hobby':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                hobby += goal_value
                
            elif goal.goal_type == 'Building/Creating Somthing':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                building += goal_value
                
            elif goal.goal_type == 'Education/Self Improvement':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                education += goal_value
                
            elif goal.goal_type == 'Volunteering':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                volunteering += goal_value
                
            elif goal.goal_type == 'Other':
                if type == 1:
                    goal_value = goal.cost
                elif type == 2:
                    goal_value = goal.hours
                elif type == 3:
                    goal_value = goal.time
                else:
                    print "You fucked up... Woops!"
                    
                other +=goal_value
                
            else:
                print "Houston we've got a problem"
                
                
        totals ={}
        totals['Travel'] = float(travel)/float(sum_of_all)*100
        totals['Purchases'] = float(purchase)/float(sum_of_all)*100
        totals['Career'] = float(career)/float(sum_of_all)*100
        totals['Extreme Sports'] = float(extreme)/float(sum_of_all)*100
        totals['Family/Social'] = float(family)/float(sum_of_all)*100
        totals['Relationships'] = float(relationship)/float(sum_of_all)*100
        totals['Exercise/Health'] = float(health)/float(sum_of_all)*100
        totals['Improving Skills'] = float(skill)/float(sum_of_all)*100
        totals['Hobbys'] = float(hobby)/float(sum_of_all)*100
        totals['Building/Creating Somthing'] = float(building)/float(sum_of_all)*100
        totals['Education/Self Improvement'] = float(education)/float(sum_of_all)*100
        totals['Volunteering'] = float(volunteering)/float(sum_of_all)*100
        totals['Other'] = float(other)/float(sum_of_all)*100
  
        return totals
        
    #-----------------Passed Through to Template (simple)---------------
    
    #General Information Passed Through to Template
    user = UserProfile.objects.get(pk = request.user.id)
    all_goals = BucketListItem.objects.all().filter(crossed_off = False)
    mylist = BucketListItem.objects.all().filter(pub_by = user, crossed_off = False)
    total_cost = BucketListItemListSum(mylist, 'cost')
    total_hours = BucketListItemListSum(mylist, 'hours')
    total_time = BucketListItemListSum(mylist, 'time')
    total_number_of_items = float(len(mylist))
    age = float(user.age)
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
        
        
        
    #Distribution of Users Goal Types by Percentage    
    goal_type_percentages = GoalTypePercentages(mylist)
    goal_type_percentages_cost = MoreGoalTypePercentages(mylist, 1)
    goal_type_percentages_hours = MoreGoalTypePercentages(mylist, 2)
    goal_type_percentages_time =MoreGoalTypePercentages(mylist, 3)
    
    
    #Most Common Goal Type
    most_common_goal = goal_type_percentages[1]
    goal_type_percentages = goal_type_percentages[0]
    
    most_common_goal_percent = most_common_goal[1]
    most_common_goal = most_common_goal[0]
    
    
    #Distribution of All Users Goal Types by Percentage (cost, hours, and time)
    all_goal_type_percentages_cost = MoreGoalTypePercentages(all_goals, 1)
    
    all_goal_type_percentages_hours = MoreGoalTypePercentages(all_goals, 2)
    
    all_goal_type_percentages_time = MoreGoalTypePercentages(all_goals, 3)

    

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
                     'most_difficult_goal_percentage': most_difficult_goal_percentage,
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
                     'goal_type_percentages': goal_type_percentages,
                     'goal_type_percentages_cost': goal_type_percentages_cost,
                     'goal_type_percentages_hours': goal_type_percentages_hours,
                     'goal_type_percentages_time': goal_type_percentages_time,
                     'all_goal_type_percentages_cost': all_goal_type_percentages_cost,
                     'all_goal_type_percentages_hours': all_goal_type_percentages_hours,
                     'all_goal_type_percentages_time': all_goal_type_percentages_time,
                     
                     #----------------Most Popular Category----------
                     'most_common_goal': most_common_goal,
                     'most_common_goal_percent': most_common_goal_percent,
                     
                        
                        
                     
                    }
                    
    return render(request, 'BucketList/recommendation.html', context)
    
    
    
@login_required
def my_list_stats(request):
    #General statistics about the current users Bucket List
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    total_cost = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('cost'))
    total_time = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('time'))
    total_crossed_off = BucketListItem.objects.all().filter(pub_by = request.user.id).aggregate(Sum('crossed_off'))
    cost_per_list_item = total_cost['cost__sum']/personal_list.count()
    time_per_list_item = total_time['time__sum']/personal_list.count()
    
    context = {'personal_list': personal_list,
                      'user': request.user.username,
                      'total_cost': total_cost['cost__sum'],
                      'total_time': total_time['time__sum'],
                      'total_crossed_off': total_crossed_off['crossed_off__sum'],
                      'cost_per_list_item': cost_per_list_item,
                      'time_per_list_item': time_per_list_item,
                      }
                      
    return render(request, 'BucketList/my_list_stats.html', context)
    
    
    
@login_required
def view_my_list_item(request, id):
    #View of a current users Bucket List Item with options to cross off or edit the Bucket List Item
    logged_in = request.user.id
    item = BucketListItem.objects.filter(pk = id)
    context = {'logged_in': logged_in,
                      'item': item[0],
                    }
    return render(request, 'BucketList/view_my_list_item.html', context)
    
    
    
@login_required
def cross_off_my_list_item(request, id):
    #The view that crosses off the Bucket List Item
    item = BucketListItem.objects.get(pk = id)
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
            return HttpResponseRedirect('/bucketlist/mylist/')
    else:
        form = BucketListItemForm()
            
    args = {}

    args['form'] = form
        
    return render(request, 'BucketList/create_item.html', args)
        
                
@login_required
def edit_bucket_list_item(request, id):
    #This view lets the user edit their Bucket List Item and directs them to other forms necessary to make the changes needed
    item = BucketListItem.objects.get(pk = id)
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
        context = {'form': form,
                           'id': item.id,
                          }

        
    return render(request, 'BucketList/edit_bucket_list_item.html', context)

    
@login_required
def edit_profile(request):
    #A view that allows the user to edit their current profile information
    current_user = UserProfile.objects.get(pk = request.user.id)
    if request.method == "POST":
        form = UserProfileEditForm(request.POST)
        if form.is_valid():
            new_age = form.cleaned_data['new_age']
            new_life_expectancy = form.cleaned_data['new_life_expectancy']
            new_yearly_earnings = form.cleaned_data['new_yearly_earnings']
            new_hourly_wage = form.cleaned_data['new_hourly_wage']
            current_user.yearly_earnings = new_yearly_earnings
            current_user.hourly_wage = new_hourly_wage
            current_user.life_expectancy = new_life_expectancy
            current_user.age = new_age   
            current_user.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
    else:
        form = UserProfileEditForm({'new_age': current_user.age, 'new_life_expectancy': current_user.life_expectancy, 'new_yearly_earnings': current_user.yearly_earnings, 'new_hourly_wage': current_user.hourly_wage})
        
        context = {'form': form,
                        }

    return render(request, 'BucketList/edit_user_profile.html', context)
    

    
        