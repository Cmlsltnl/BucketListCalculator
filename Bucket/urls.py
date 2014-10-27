from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^bucketlist/', include('BucketList.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'Bucket.views.login'),
    url(r'^accounts/auth/$', 'Bucket.views.auth_view'),
    url(r'^accounts/logout/$', 'Bucket.views.logout'),
    url(r'^accounts/loggedin/$', 'Bucket.views.loggedin'),
    url(r'^accounts/invalid/$', 'Bucket.views.invalid_login'),
    url(r'^accounts/register/$', 'Bucket.views.register_user'),
    url(r'^accounts/register_success/$', 'Bucket.views.register_success'),
    url(r'^accounts/edit/$', 'Bucket.views.edit'),
    url(r'^avatar/', include('avatar.urls')),
    url(r'^messages/', include('django_messages.urls')),
    url(r'^password/',include('password_reset.urls')),
)

if settings.DEBUG:
    #static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})
    )