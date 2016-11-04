from django.shortcuts import render
from EventLite.models import *
from django.contrib.auth.models import User
from sys import stderr


def index(request):
    b = Buyer(points=0)
    user = User(username='', password='')
    u = UserDetail(user = user, email='', social_login=False)
    print("Hello", file=stderr)
    return render(request, 'index.html', {'user': request.user})


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})


def registration(request):
    return render(request, 'registration.html', {})

def view_events(request):
    return render(request, 'view-events.html', {})