from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from Bucket.forms import MyRegistrationForm
from BucketList.forms import UserProfileForm

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
    return render_to_response('loggedin.html',
                                              {'full_name': request.user.username})
                                              
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
    
        
 
 
 
 