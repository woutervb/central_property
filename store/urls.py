from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('store.views',
    url(r'^$', redirect_to, {'url' : '/admin'}),
    url(r'^(?P<object_ref>[\w\/]+)', 'store'),
)
