from django.db import models
from django.utils import timezone
import datetime
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

class BucketListItem(models.Model):
    """The Model that defines each Bucket List Item"""
    text = models.CharField(max_length = 200)
    pub_by = models.ForeignKey(User,editable = False)
    pub_date = models.DateTimeField(editable=False)
    cost = models.CharField(max_length = 20, editable = False)
    time = models.CharField(max_length = 20, editable = False)
    hours = models.CharField(max_length = 20, editable = False)
    crossed_off = models.BooleanField(editable = False)
    goal_type = models.CharField(choices = CHOICES, max_length = 200)
        
    def __unicode__(self):
        return self.text
    
    def recently_added(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days = 1)
    
    recently_added.boolean = True

    def save(self):
        if not self.id:
            self.pub_date = timezone.now()
        super(BucketListItem, self).save()
        
class UserProfile(models.Model):    
    """Model that defines the User Profile"""
    user = models.OneToOneField(User, editable = False)
    age = models.CharField(max_length = 3)
    life_expectancy = models.CharField(max_length = 3)  

    def __unicode__(self):
        return self.user
        
        
        
        
        