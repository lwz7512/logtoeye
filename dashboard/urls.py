__author__ = 'lwz'

from django.conf.urls import patterns, include, url
import socketio.sdjango

urlpatterns = patterns("dashboard.views",
                       url("^socket\.io", include(socketio.sdjango.urls)),
                       url(r'dashboard/$', 'dashboard', name='dashboard')
                       )

