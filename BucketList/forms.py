from django import forms
from models import BucketListItem, UserProfile
from django.contrib.auth.models import User

CHOICES = (
    ('Travel','Travel'),
    ('Purchase', 'Purchase'), 
    ('Career', 'Career'), 
    ('Extreme Sport', 'Extreme Sport'), 
    ('Family/Social', 'Family/Social'), 
    ('Relationship', 'Relationship'), 
    ('Exercise/Health', 'Exercise/Health'), 
    ('Improving a Skill', 'Improving a Skill'), 
    ('Hobby', 'Hobby'),
    ('Building/Creating Somthing', 'Building/Creating Somthing'),
    ('Education/Self Improvement', 'Education/Self Improvement'),
    ('Volunteering', 'Volunteering'),
    ('Other', 'Other'),
    
    )
    
    
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
        

class BucketListItemEditForm(forms.ModelForm):
    """Form used to edit a Bucket List Item"""
    class Meta:
        model = BucketListItem
    
    
class CustomItemEditForm(forms.Form):
    """The form used to create the Bucket List Item once the goal type is already decided upon"""
    new_cost = forms.FloatField(label = 'cost')
    new_time = forms.FloatField(label = 'time')
    new_hours = forms.FloatField(label = 'hours')
    
    
    
