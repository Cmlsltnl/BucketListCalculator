from django.contrib import admin
from BucketList.models import BucketListItem, UserProfile, Comment


class BucketListItemAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Text',              {'fields': ['text']}),
        ('Cost',              {'fields': ['cost']}),
        ('Time',              {'fields': ['time']}),
    ]
    readonly_fields = ('pub_date',)
    list_display = ['text', 'pub_date', 'pub_by', 'cost', 'time', 'hours', 'crossed_off', 'goal_type']
    list_filter = ['pub_date', 'pub_by', 'cost', 'time']
    search_fields = ['text', 'pub_by']
  
admin.site.register(BucketListItem, BucketListItemAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    fieldsets = [ 
        ('User',            {'fields': ['user']}),
        ('Age',            {'fields': ['age']}),
        ('Life Expectancy',            {'fields': ['life_expectancy']}),
    ]
    readonly_fields = ('user', 'age', 'life_expectancy', 'yearly_earnings', 'hourly_wage', 'birth_date', 'include_retirement', 'retirement', 'retirement_savings')
    list_display = ['user', 'age', 'life_expectancy', 'yearly_earnings', 'hourly_wage', 'birth_date', 'include_retirement', 'retirement', 'retirement_savings']
    
admin.site.register(UserProfile, UserProfileAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ['body', 'item', 'author', 'created']
    
admin.site.register(Comment, CommentAdmin)



    
    
    