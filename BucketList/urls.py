from django.conf.urls import patterns, url
from BucketList import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^stats/$', views.index_stats, name='index stats'),
    url(r'^item/(?P<id>\w+)/', views.index_items, name = 'index items'),
    url(r'^item/(?P<id>\w+)/comment', views.add_item_comment, name = 'add item comments'),
    url(r'^userstats/(?P<id>\w+)/', views.user_stats, name='user profile'),
    url(r'^create/$', views.create, name='create'),
    url(r'^create/(?P<id>\w+)/', views.create_specific_item, name = 'create specific item'),
    url(r'^mylist/$', views.my_list, name='mylist'),
    url(r'^mylist/stats/$', views.my_list_stats, name='mylist stats'),
    url(r'^mylist/edit/(?P<id>\w+)/', views.edit_bucket_list_item, name = 'edit my list item'),
    url(r'^mylist/view/(?P<id>\w+)/', views.view_my_list_item, name = 'view my list item'),
    url(r'^mylist/uncross/(?P<id>\w+)/', views.uncross_my_list_item, name = 'uncross my list item'),
    url(r'^mylist/crossoff/(?P<id>\w+)/', views.cross_off_my_list_item, name = 'cross off'),
    url(r'^mylist/deleteitem/(?P<id>\w+)/', views.delete_my_list_item, name = 'delete list item'),
    url(r'^mylist/recommendation/$', views.recommendation, name = 'recommendation'),
    url(r'^profile/edit/$', views.edit_profile, name = 'edit profile'),
)

