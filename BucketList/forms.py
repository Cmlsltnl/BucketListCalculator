from django import forms
from models import BucketListItem, UserProfile
from django.contrib.auth.models import User

class BucketListItemForm(forms.ModelForm):
    """The main form to create a Bucket List Item"""
    class Meta:
        model = BucketListItem


class UserProfileForm(forms.ModelForm):
    """The main form to create a User Profile"""
    class Meta:
        model = UserProfile
        
        
class UserProfileEditForm(forms.Form):
    """Form used to edit the User Profile"""
    new_age = forms.CharField(label='New Age', max_length = 200)
    new_life_expectancy = forms.CharField(label = 'New Life Expectancy', max_length = 3)
        

class BucketListItemEditForm(forms.Form):
    """Form used to edit a Bucket List Item"""
    new_text = forms.CharField(max_length = 200)
    new_cost = forms.CharField(max_length = 10)
    new_time = forms.CharField(max_length = 10)
    new_hours = forms.CharField(max_length = 10)
    
    
class CustomItemEditForm(forms.Form):
    """The form used to create the Bucket List Item once the goal type is already deicded upon"""
    new_cost = forms.FloatField(label = 'cost')
    new_time = forms.FloatField(label = 'time')
    new_hours = forms.FloatField(label = 'hours')
    
    
    
