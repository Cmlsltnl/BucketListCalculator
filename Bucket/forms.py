from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class MyRegistrationForm(UserCreationForm):
    #Form that creates a user account
    email = forms.EmailField(required = True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def save(self, commit = True):
        user = super(MyRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            
        return user
        
        
class EditRegistrationForm(forms.Form):
    password = forms.CharField(widget = forms.PasswordInput, required = False, label = 'Password')
    email = forms.EmailField(required = False, label = 'Current Email Address')
    new_email = forms.EmailField(required = False, label = 'New Email Address')
    new_password1 = forms.CharField(widget = forms.PasswordInput, required = False, label = 'New Password')
    new_password2 = forms.CharField(widget = forms.PasswordInput, required = False, label = 'Confirm New Password')
        

        