from django.shortcuts import render
from EventLite.models import *
from django.contrib.auth.models import User
from sys import stderr
# Create your views here.


def index(request):
    return render(request, 'index.html', {'user': request.user})


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})


def registration(request):
    return render(request, 'registration.html', {})


def view_events(request):
    return render(request, 'view-events.html', {})

# social login aftermath
# need to handle case where user hasn't activated account#
# Should be atomic
# 
def login_next(request):
    if(UserDetail.objects.filter(user=request.user).count()==0):
        print('no user exists')

        newProfile = UserDetail(user=request.user,social_login=True)
        newProfile.save()
    else:
        print('user exists')
    return render(request, 'loggedin.html', {})
