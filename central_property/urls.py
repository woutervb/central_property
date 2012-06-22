from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to
from django.conf import settings
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', redirect_to, {'url' : '/store'}),
    url(r'^store/', include('store.urls')),
    url(r'^fqdn/(?P<object_ref>[\w\.]+)$', 'store.foreman.fqdn'),
    url(r'^admin/', include(admin.site.urls)),
)
