from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from Bucket.forms import MyRegistrationForm, EditRegistrationForm
from BucketList.forms import UserProfileForm
from BucketList.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def login(request):
    #The user login page
    c = {}
    c.update(csrf(request))
    return render_to_response('login.html', c)
    
def auth_view(request):
    #Authenticates to make sure the information is correct
    username = request.POST.get('username', ' ')
    password = request.POST.get('password', ' ')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
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
    return render_to_response('invalid_login.html')
    
def logout(request):
    #Screen displayed if user is logged out
    auth.logout(request)
    return render_to_response('logout.html')
    
def register_user(request):
    #The view that allows the user to register
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success')
        
    args = {}
    args.update(csrf(request))
    args['form'] = MyRegistrationForm()
    return render_to_response('register.html', args)
    
    
def register_success(request):
    #Screen returned if registration was a success
    return render_to_response('register_success.html')
    
    
@login_required        
def edit(request):
    #The view that allows the user to edit their account information
    if request.method == 'POST':
        form = EditRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id = request.user.id)
            username = user.username
            email = form.cleaned_data['email']
            new_email = form.cleaned_data['new_email']
            password = form.cleaned_data['password']
            new_password1 = form.cleaned_data['new_password1']               
            new_password2 = form.cleaned_data['new_password2']
            email_match = email == user.email
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
                            return render_to_response('edit_success.html', args)
                        except:
                            user.email = new_email
                            user.save() 
                            change_email = True
                    else:
                        args['no_email_match'] = True
                        return render_to_response('edit_success.html', args)
            
                if new_password1 and new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    change_password = True                                
                 
                if change_email or change_password:
                    
                    args['change_email'] = change_email
                    args['change_password'] = change_password
                    return render_to_response('edit_success.html', args)
            else:
                args['pass_match'] = pass_match
                return render_to_response('edit_success.html', args)
                    
    args = {}
    args.update(csrf(request))
    args['form'] = EditRegistrationForm()
    return render_to_response('edit.html', args)
 
    
    