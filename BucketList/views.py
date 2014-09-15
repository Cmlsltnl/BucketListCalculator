from django.shortcuts import render
from django.http import HttpResponse
from BucketList.models import BucketListItem, UserProfile, Comment
from django.contrib import auth
from forms import BucketListItemForm, UserProfileForm, UserProfileEditForm, BucketListItemEditForm, CustomItemEditForm, CommentForm
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required



def index(request):
    """The main Bucket List Page View, sorted by pubdate so the most recent are at the top"""
    all_list_items = BucketListItem.objects.all().order_by('-pub_date')
    
    context = {'all_list_items': all_list_items}
    
    return render(request, 'BucketList/index.html', context)
    
    
def index_items(request, id):
    """When a user clicks on a Bucket List Item on the index page it will take them here with a brief overview of that items information"""
    item = BucketListItem.objects.all().filter(pk = id)
    form = CommentForm()
    comments = Comment.objects.all().filter(item = item)
    
    context = {'item': item[0],
                      'id': id,
                      'comments': comments,
                      'form': form,
                      }
    return render(request, 'BucketList/index_items.html', context)
    

@login_required
def add_item_comment(request, id):
    #Add a comment to any Users BucketListItem
    current_user = UserProfile.objects.get(pk = request.user.id)
    current_item = BucketListItem.objects.get(pk = id)
    form = CommentForm(request.POST)
    if form.is_valid():
        body = form.cleaned_data['body']
        my_model = form.save(commit = False)
        my_model.created = timezone.now()
        my_model.author = current_user.user
        my_model.item = current_item
        my_model.body = body
        my_model.save()
    return HttpResponseRedirect("/bucketlist/item/%s/" % id)

    
    
@login_required
def user_stats(request, id):
    """A public stats/profile page that displays their basic profile information as well as their bucket list"""
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
    """This page compiles interesting statistics about all of the Bucket List Items on the main index page and displays that information"""
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
    """The current users personal Bucket List view with links to create more list items or learn statistics about their list"""
    personal_list = BucketListItem.objects.all().filter(pub_by = request.user.id)
    
    context = {'personal_list': personal_list,
                      'user': request.user.username
                    }
                      
    return render(request, 'BucketList/mylist.html', context)
    
    
@login_required
def recommendation(request):
    """This view takes the users list items and turns it into a convenient display of the stats in a user friendly form, basically this view is the main reason everything else in this web app exists. """
    
    """---------------Important Recommendation Functions-------------"""  
    
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
        """Determines how difficult the goal is by returning the total amount of hours the goal will take.  Returns cost in hours by utilizing users hourly wage.  Returns 17 hours per day goal takes (not 24 because of time accounted for sleep and other free time"""
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
        """Figures out the distribution of different goal types and returns the percentage amount of each goal category"""
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
        return totals        
        

            
        
    """-----------------Passed Through to Template (simple)---------------"""
    
    """General Information Passed Through to Template"""
    user = UserProfile.objects.get(pk = request.user.id)
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
    
    """Calculated Information Passed Through to Template"""
    accomplish_per_year = total_number_of_items/years_left
    days_per_goal = days_left/total_number_of_items
    cost_per_year = total_cost/years_left
    days_per_year = total_time/years_left
    hours_per_year = total_hours/years_left
    hours_per_month = hours_per_year/12
    hours_per_week = hours_per_year/52
    cost_of_average_goal = float(total_cost/total_number_of_items)
    percent_of_yearly_wage = (cost_per_year/yearly_earnings)*100

    """----------------Passed Through to Template (unique)--------------"""  
     
    """Create List Of Bucket List Items from Most to Least Difficult, using GoalDifficulty Function"""
    dict_with_difficulty = {}
    
    for goal in mylist:
        dict_with_difficulty.update(GoalDifficulty(goal, hourly_wage))
        
    list_with_difficulty = []
    
    while len(dict_with_difficulty) > 0:
        item = max(dict_with_difficulty, key=dict_with_difficulty.get)
        list_with_difficulty.append(item)
        del dict_with_difficulty[item]
    
    
    """Sorts list_with_difficulty from above into two lists, one of the top five most difficult BucketListItems and another with the five easiest goals"""
    top_five_most_difficult = []
    bottom_five_least_difficult = []
    
    for item in list_with_difficulty[:5]:
        top_five_most_difficult.append(item)
        
    list_with_difficulty.reverse()
    
    for item in list_with_difficulty[:5]:
        bottom_five_least_difficult.append(item)
    
    
    """Different Goal Types by Percentage"""
    goal_type_percentages = GoalTypePercentages(mylist)
            
    


    """--------------------Passed To Template-----------------------"""               
    
    context = {'user': user,
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
                     
                     
                     'list_with_difficulty': list_with_difficulty,
                     'top_five_most_difficult': top_five_most_difficult,
                     'bottom_five_least_difficult': bottom_five_least_difficult,
                     'goal_type_percentages': goal_type_percentages,
                     
                    }
                    
    return render(request, 'BucketList/recommendation.html', context)
    
    
    
@login_required
def my_list_stats(request):
    """General statistics about the current users Bucket List"""
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
    """View of a current users Bucket List Item with options to cross off or edit the Bucket List Item"""
    logged_in = request.user.id
    item = BucketListItem.objects.filter(pk = id)
    context = {'logged_in': logged_in,
                      'item': item[0],
                    }
    return render(request, 'BucketList/view_my_list_item.html', context)
    
@login_required
def cross_off_my_list_item(request, id):
    """The view that crosses off the Bucket List Item"""
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
    """The view that uncrosses off the Bucket List Item"""
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
    """The view that uncrosses off the Bucket List Item"""
    item = BucketListItem.objects.get(pk = id)
    title = item.text
    item.delete()
    
    context = {'title': title,
                      'User': User,
                    }
                    
    return render(request, 'BucketList/delete.html', context)
    
    
    
@login_required
def create(request):
    """Creates a Bucket List Item, the user only fills out the Name and Type of the item while the rest of the fields are auto-filled: publication date, published by, crossed off, time, hours, and cost """
    if request.POST:
        form = BucketListItemForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            my_model = form.save(commit = False)
            my_model.pub_by = user
            my_model.crossed_off = False
            my_model.time = 0
            my_model.hours = 0
            my_model.cost = 0
            my_model.save()
            return HttpResponseRedirect('/bucketlist/create/%s' % my_model.id)
    else:
        form = BucketListItemForm()
            
    args = {}
    args.update(csrf(request))
    args['form'] = form
        
    return render_to_response('BucketList/create_item.html', args)
    

@login_required
def create_specific_item(request, id):
    """Taken here immediately after creating the bucket list item, takes user to a specific view based upon what goal type they input and then gives them another form to give more detail about the goal"""
    item1 = BucketListItem.objects.all().filter(pk = id)
    item2 = item1[0]
    goal_type = item2.goal_type
    
    if goal_type == 'Travel':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_time = form.cleaned_data['new_time']
                new_cost = form.cleaned_data['new_cost']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})    
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/travel.html', args)
    
        
    elif goal_type == 'Purchase':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/purchase.html', args)

        
    elif goal_type == 'Career':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/career.html', args)
        
        
    elif goal_type == 'Extreme Sport':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/extremesport.html', args)
        
        
    elif goal_type == 'Family/Social':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/familysocial.html', args)
        
        
    elif goal_type == 'Relationship':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/relationship.html', args)
        
        
    elif goal_type == 'Exercise/Health':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/exercisehealth.html', args)
        
    elif goal_type == 'Improving a Skill':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/improveskill.html', args)
        
    elif goal_type == 'Hobby':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/hobby.html', args)
        
    elif goal_type == 'Building/Creating Somthing':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/buildcreate.html', args)
        
        
    elif goal_type == 'Education/Self Improvement':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/education.html', args)
        
        
    elif goal_type == 'Volunteering':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/volunteering.html', args)    
        
    elif goal_type == 'Other':
        if request.POST:
            form = CustomItemEditForm(request.POST)
            if form.is_valid():
                new_cost = form.cleaned_data['new_cost']
                new_time = form.cleaned_data['new_time']
                new_hours = form.cleaned_data['new_hours']
                item = BucketListItem.objects.filter(pk = id)
                item = item[0]
                item.time = new_time
                item.hours = new_hours
                item.cost = new_cost
                item.save()
            return HttpResponseRedirect('/bucketlist/mylist/')
            
        else:
            form = CustomItemEditForm({'new_hours': item2.hours, 'new_cost': item2.cost, 'new_time': item2.time})     
            
        url = ('bucketlist/create/%s' % id)            
        args = {}
        args.update(csrf(request))
        args['form'] = form
        args['id'] = id
        args['url'] = url

        
        return render_to_response('BucketList/item_creation/other.html', args)    
    
                
                
@login_required
def edit_profile(request):
    """A view that allows the user to edit their current profile information"""
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
        
    return render(request, 'BucketList/edit_user_profile.html', {'form': form})
    
    
@login_required
def edit_bucket_list_item(request, id):
    """This view lets the user edit their Bucket List Item and directs them to other forms necessary to make the changes needed"""
    item = BucketListItem.objects.get(pk = id)
    if request.method == "POST":
        form = BucketListItemEditForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            goal_type = form.cleaned_data['goal_type']
            item.text = text
            item.goal_type = goal_type
            item.pub_date = timezone.now()
            item.save()
            return HttpResponseRedirect('/bucketlist/create/%s' % item.id)
    else:
        form = BucketListItemEditForm({'text': item.text, 'goal_type': item.goal_type})
        
    return render(request, 'BucketList/edit_bucket_list_item.html', {'form': form, 'id': item.id})
    
    
        