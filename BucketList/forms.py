from django import forms
from models import BucketListItem, UserProfile, Comment
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
    #The main form to create a Bucket List Item
    class Meta:
        model = BucketListItem


class UserProfileForm(forms.ModelForm):
    #The main form to create a User Profile
    class Meta:
        model = UserProfile
        
        
class CommentForm(forms.ModelForm):
    #Form to create a comment
    class Meta:
        model = Comment
        exclude = ['post', 'author', 'item']
        
    

    
class UserProfileEditForm(forms.Form):
    #Form used to edit the User Profile
    new_age = forms.CharField(label='Age', max_length = 200)
    new_life_expectancy = forms.CharField(label = 'Age You Will Be Done', max_length = 3)
    new_yearly_earnings = forms.CharField(label = 'Yearly Earnings', max_length = 8)
    new_hourly_wage = forms.CharField(label = 'Hourly Wage', max_length = 3)
    new_birth_date = forms.DateField(label = 'Birth Date')
        

class BucketListItemEditForm(forms.ModelForm):
    #Form used to edit a Bucket List Item
    class Meta:
        model = BucketListItem
    
    
class CustomItemEditForm(forms.Form):
    #The form used to create the Bucket List Item once the goal type is already decided upon
    new_cost = forms.FloatField(label = 'cost')
    new_time = forms.FloatField(label = 'time')
    new_hours = forms.FloatField(label = 'hours')
    
    
    
