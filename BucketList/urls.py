from django.conf.urls import patterns, url
from BucketList import views

urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),
    url(r'^item/(?P<id>\w+)/delete-comment/', views.delete_comment, name = 'delete comment'),
    url(r'^item/(?P<id>\w+)/', views.index_items, name = 'index items'),
    url(r'^userstats/(?P<id>\w+)/', views.user_stats, name='user profile'),
    url(r'^create/$', views.create, name='create'),
    url(r'^mylist/$', views.my_list, name='mylist'),
    url(r'^mylist/edit/(?P<id>\w+)/', views.edit_bucket_list_item, name = 'edit my list item'),
    url(r'^mylist/uncross/(?P<id>\w+)/', views.uncross_my_list_item, name = 'uncross my list item'),
    url(r'^mylist/crossoff/(?P<id>\w+)/', views.cross_off_my_list_item, name = 'cross off'),
    url(r'^mylist/deleteitem/(?P<id>\w+)/', views.delete_my_list_item, name = 'delete list item'),
    url(r'^mylist/recommendation/$', views.recommendation, name = 'recommendation'),
    url(r'^mylist/compare/(?P<id>\w+)/', views.compare_my_list_item, name = 'compare list item'),
    url(r'^profile/edit/$', views.edit_profile, name = 'edit profile'),
    url(r'^tutorial/$', views.tutorial, name = 'tutorial'),
    url(r'^about/$', views.about_us, name = 'about us'),
    url(r'^contact/$', views.contact_us, name = 'contact'),
    url(r'^terms/$', views.terms_and_conditions, name = 'terms and conditions'),
    url(r'^privacypolicy/$', views.privacy_policy, name = 'privacy policy'),
    url(r'^search/$', views.search, name = 'search'),
)

