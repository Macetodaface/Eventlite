from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from sys import stderr

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate,logout
from django.db import transaction

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required


from EventLite.models import *
# Create your views here.


def index(request):
    return render(request, 'index.html')


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})


def registration(request):
    return render(request, 'registration.html', {})

@login_required
def view_events(request):
    return render(request, 'view-events.html', {'user':request.user})

@login_required
def logoutUser(request):
    logout(request)
    return redirect('/')

# social login aftermath
# need to handle case where user hasn't activated account#
# Should be atomic
@transaction.atomic
def social_login(request):
    if(UserDetail.objects.filter(user__email=request.user.email).count()==0):
        print('no user exists')
        newBuyer = Buyer()
        newSeller = Seller()
        newBuyer.save()
        newSeller.save()
        newProfile = UserDetail(user=request.user,social_login=True,buyer=newBuyer,seller=newSeller)
        newProfile.save()
    else:
        print('user exists')
        # check activation
        userDetail = UserDetail.objects.get(user__email=request.user.email)
        print userDetail
        if(userDetail.user.is_active==False):
            # User has logged in using social auth without activation from link
            # 1. invalidate the activation key.
            # 2. is_active = True
            # 3. save
            userDetail.user.activation_key = ''
            userDetail.user.is_active=True
            userDetail.user.save()
            userDetail.save()


    return render(request, 'view-events.html', {})
