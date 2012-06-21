from django.conf.urls import patterns, include, url

urlpatterns = patterns('store.views',
#    url(r'^$', 'index'),
    url(r'^(?P<object_ref>[\w\/]+)', 'store'),
)
