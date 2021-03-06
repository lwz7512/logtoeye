from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'dashboard.views.home', name='home'),
                       url(r'^ui/', 'dashboard.views.builder', name='builder'),
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url("", include("dashboard.urls")),
                       )
