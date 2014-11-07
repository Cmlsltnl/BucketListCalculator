from django import forms
from models import BucketListItem, UserProfile, Comment
from django.contrib.auth.models import User
from validators import validate_positive
from django.forms.extras.widgets import SelectDateWidget

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
    YEARS = ['1900', '1901', '1902', '1903', '1904', '1905', '1906', '1907', '1908', '1909', '1910', '1911', '1912', '1913', '1914', '1915', '1916', '1917', '1918', '1919', '1920', '1921', '1922', '1923', '1924', '1925', '1926', '1927', '1928', '1929', '1930', '1931', '1932', '1933', '1934', '1935', '1936', '1937', '1938', '1939', '1940', '1941', '1942', '1943', '1944', '1945', '1946', '1947', '1948', '1949', '1950', '1951', '1952', '1953', '1954', '1955', '1956', '1957', '1958', '1959', '1960', '1961', '1962', '1963', '1964', '1965', '1966', '1967', '1968', '1969', '1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978',
    '1979', '1980', '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014']
  
    
    new_birth_date = forms.DateField(label = 'Your Birth Date', widget=SelectDateWidget(years = YEARS))
    new_life_expectancy = forms.IntegerField(label = 'Age You Will Be Done', validators = [validate_positive])
    new_yearly_earnings = forms.IntegerField(label = 'Yearly Earnings', validators = [validate_positive])
    new_hourly_wage = forms.FloatField(label = 'Hourly Wage', validators = [validate_positive])
    new_include_retirement = forms.BooleanField(label = 'Include Retirement', required = False)
    new_retirement = forms.IntegerField(label = 'Retirement Age', validators = [validate_positive])
    new_retirement_savings = forms.IntegerField(label = 'Retirement Savings', validators = [validate_positive])
        
        

class BucketListItemEditForm(forms.ModelForm):
    #Form used to edit a Bucket List Item
    class Meta:
        model = BucketListItem
    
    
    
    
    
