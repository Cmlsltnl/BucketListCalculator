from django.db import models
from django.utils import timezone
from datetime import datetime
from datetime import date
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.signals import request_finished
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from Bucket.forms import MyRegistrationForm, UserCreationForm


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
    ('Building/Creating Something', 'Building/Creating Something'),
    ('Education/Self Improvement', 'Education/Self Improvement'),
    ('Volunteering', 'Volunteering'),
    ('Other', 'Other'),
    
    )

class BucketListItem(models.Model):
    #The Model that defines each Bucket List Item
    text = models.CharField(max_length = 200)
    pub_by = models.ForeignKey(User,editable = False)
    pub_date = models.DateTimeField(editable=False)
    goal_type = models.CharField(choices = CHOICES, max_length = 200)
    cost = models.IntegerField(max_length = 20)
    time = models.IntegerField(max_length = 20)
    hours = models.IntegerField(max_length = 20)
    crossed_off = models.BooleanField(editable = False, default = False)
    how_many_items = models.IntegerField(editable = False, default = 1)
    
        
    def __unicode__(self):
        return self.text
    
    def save(self):
        if not self.id:
            self.pub_date = timezone.now()
        super(BucketListItem, self).save()
        
        
        
class UserProfile(models.Model):    
    #Model that defines the User Profile
    user = models.OneToOneField(User, editable = False)
    life_expectancy = models.CharField(max_length = 3, default = 0)
    yearly_earnings = models.CharField(max_length = 8, default = 0)
    hourly_wage = models.CharField(max_length = 3, default = 0)
    birth_date = models.DateField(default = datetime.now)
    include_retirement = models.BooleanField(default = False)
    retirement = models.CharField(max_length = 3, default = 0)
    retirement_savings = models.CharField(max_length = 10, default = 0)
    
    
    def age(self):
        return FindAge(self.birth_date)
        
    def __unicode__(self):
        return self.user
        
    
    
      
class Comment(models.Model):
    #Model that defines the Commenting system
    created = models.DateTimeField(editable =False)
    author = models.CharField(max_length = 100, editable = False)
    body = models.TextField()
    item = models.ForeignKey(BucketListItem)
    
    def __unicode__(self):
        return self.body
        
    
    
@receiver(post_save, sender = User)
def my_callback(sender, instance, created, **kwargs):
    #Watches for User Creation then automatically creates a UserProfile for the User Created
    if created:
        UserProfile.objects.create(user = instance)


        
        