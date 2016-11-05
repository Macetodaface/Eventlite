"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from EventLite import views

urlpatterns = [
    url(r'^$', views.index),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^base', views.base, name='base'),
    url(r'^post-event', views.post_event, name='post-event'),
    url(r'^registration', views.registration, name='registration'),
    url(r'^view-events', views.view_events, name='view-events'),
    url(r'^loggedin', views.social_login, name='loggedin'),
    url(r'^logout', views.logoutUser, name='logout'),
]
