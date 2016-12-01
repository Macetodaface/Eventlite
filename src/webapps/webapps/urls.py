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


import django.contrib.auth.views

import EventLite.views.eventViews as eventViews
import EventLite.views.accountViews as accountViews
import EventLite.views.views as views


urlpatterns = [

    url(r'^$', eventViews.view_events,name='home'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^base', views.base, name='base'),
    url(r'^post-event', eventViews.post_event, name='post-event'),
    url(r'^registration', accountViews.registration, name='registration'),
    url(r'^seat-layout/(?P<id>.+)',eventViews.getSeatLayout,name = 'seatLayout'),
    url(r'^view-events', eventViews.view_events, name='view-events'),
    url(r'^my-events', eventViews.my_events, name='my-events'),
    url(r'^event-info/(?P<id>.+)', eventViews.event_info, name='event-info'),
    url(r'^ticket-type-html/(?P<id>.+)', eventViews.ticket_type_html, name='ticket-type-html'),
    url(r'^buy-ticket/(?P<id>.+)', eventViews.buy_ticket, name='buy-ticket'),
    url(r'^add-review/(?P<id>.+)', eventViews.add_review, name='add-review'),
    url(r'^profile/(?P<user>.+)', accountViews.profile, name='profile'),
    url(r'^login/$', accountViews.manual_login, name='login'),
    url(r'^loggedin', accountViews.social_login, name='loggedin'),
    url(r'^logout', accountViews.logoutUser, name='logout'),
    url(r'^activate$', accountViews.activate, name='activate'),
    url(r'^recover-password', accountViews.recover_password, name='recover-password'),
    url(r'^new_password/(?P<key>.+)', accountViews.new_password, name='new-password'),
    url(r'^search-events/$', eventViews.search_events, name='search-events'),
    url(r'^get-interest/(?P<id>.+)', eventViews.get_interest, name='get-interest'),
    url(r'^show-interest/(?P<id>.+)', eventViews.show_interest, name='show-interest'),
    url(r'^profile/(?P<user>[\w\.]+)', accountViews.profile, name='profile'),

]
