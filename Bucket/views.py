from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from Bucket.forms import MyRegistrationForm, EditRegistrationForm
from BucketList.forms import UserProfileForm
from BucketList.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import operator


def login(request):
    #The user login page
    c = {}
    c.update(csrf(request))
    return render(request, 'login.html', c)
    
def auth_view(request):
    #Authenticates to make sure the information is correct
    username = request.POST.get('username', ' ')
    password = request.POST.get('password', ' ')
    user1 = auth.authenticate(username=username, password=password)
    
    if user1 is not None:
        auth.login(request, user1)
        return HttpResponseRedirect('/accounts/loggedin')
    else:
        return HttpResponseRedirect('/accounts/invalid')
        
def loggedin(request):
    #Screen displayed if user is logged in correctly
    user_profile = UserProfile.objects.get(user = request.user)  
    
    if user_profile.age == 0 or user_profile.life_expectancy == 0 or user_profile.yearly_earnings == 0 or user_profile.hourly_wage == 0:
        return HttpResponseRedirect('/bucketlist/profile/edit/')
        
    else:
        return HttpResponseRedirect('/bucketlist/')
                                              
def invalid_login(request):
    #Screen displayed if there was a problem with the login information
    return render(request, 'invalid_login.html')
    
def logout(request):
    #Screen displayed if user is logged out
    auth.logout(request)
    return render(request, 'logout.html')
    
def register_user(request):
    #The view that allows the user to register
    args = {}
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success')
            
    else:
        form = MyRegistrationForm()
        
    args['form'] = form
    args.update(csrf(request))
    return render(request, 'register.html', args)
    
    
def register_success(request):
    #Screen returned if registration was a success
    return render(request, 'register_success.html')
    
    
@login_required        
def edit(request):
    #The view that allows the user to edit their account information
    if request.method == 'POST':
        form = EditRegistrationForm(request.POST)
        if form.is_valid():
            user1 = User.objects.get(id = request.user.id)
            username = user1.username
            email = form.cleaned_data['email']
            new_email = form.cleaned_data['new_email']
            password = form.cleaned_data['password']
            new_password1 = form.cleaned_data['new_password1']               
            new_password2 = form.cleaned_data['new_password2']
            email_match = email == user1.email
            pass_match = auth.authenticate(username = username, password = password)
            change_email = False
            change_password = False
            args = {}

                
            if pass_match != None:
                args['pass_match'] = pass_match
                
                if len(new_email) > 0:
                    if email_match:
                        try:
                            exists = User.objects.get(email = new_email)
                            args['email_not_unique'] = True
                            return render(request, 'edit_success.html', args)
                        except:
                            user1.email = new_email
                            user1.save() 
                            change_email = True
                    else:
                        args['no_email_match'] = True
                        return render(request, 'edit_success.html', args)
            
                if new_password1 and new_password1 == new_password2:
                    user1.set_password(new_password1)
                    user1.save()
                    change_password = True                                
                 
                if change_email or change_password:
                    
                    args['change_email'] = change_email
                    args['change_password'] = change_password
                    return render(request, 'edit_success.html', args)
            else:
                args['pass_match'] = pass_match
                return render(request, 'edit_success.html', args)
                    
    args = {}
    args.update(csrf(request))
    args['form'] = EditRegistrationForm()
    return render(request, 'edit.html', args)
 
    
    