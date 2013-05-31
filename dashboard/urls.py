__author__ = 'lwz'

from django.conf.urls import patterns, include, url
import socketio.sdjango

urlpatterns = patterns("dashboard.views",
                       url("^socket\.io", include(socketio.sdjango.urls)),
                       url(r'dashboard/$', 'dashboard', name='dashboard'),
                       url(r'report/$', 'report', name='dashboard'),
                       url(r'config/$', 'config', name='dashboard'),
                       url(r'preview/$', 'preview_report', name='preview'),
                       )

