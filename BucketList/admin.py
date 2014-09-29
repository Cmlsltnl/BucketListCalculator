from django.contrib import admin
from BucketList.models import BucketListItem, UserProfile, Comment, GoalDistributionChart


class BucketListItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Text',              {'fields': ['text']}),
        ('Cost',              {'fields': ['cost']}),
        ('Time',              {'fields': ['time']}),
    ]
    readonly_fields = ('pub_date',)
    list_display = ['text', 'pub_date', 'pub_by', 'cost', 'time', 'hours', 'recently_added', 'crossed_off', 'goal_type']
    list_filter = ['pub_date', 'pub_by', 'cost', 'time']
    search_fields = ['text', 'pub_by']
  
admin.site.register(BucketListItem, BucketListItemAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [ 
        ('User',            {'fields': ['user']}),
        ('Age',            {'fields': ['age']}),
        ('Life Expectancy',            {'fields': ['life_expectancy']}),
    ]
    readonly_fields = ('user', 'age', 'life_expectancy', 'yearly_earnings', 'hourly_wage')
    list_display = ['user', 'age', 'life_expectancy', 'yearly_earnings', 'hourly_wage']
    
admin.site.register(UserProfile, UserProfileAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['body', 'item', 'author', 'created']
    
admin.site.register(Comment, CommentAdmin)


class GoalDistributionChartAdmin(admin.ModelAdmin):
    list_display = ['goal_type', 'percentage']
    
admin.site.register(GoalDistributionChart, GoalDistributionChartAdmin)