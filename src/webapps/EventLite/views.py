from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import transaction
from string import ascii_uppercase
from random import choice
from EventLite.models import *
from EventLite.forms import *
from django.core.mail import send_mail

from sys import stderr
# Create your views here.


def index(request):
    return render(request, 'index.html', {})


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})


@transaction.atomic
def registration(request):
    url = 'registration.html'
    context = {}

    if request.method == 'GET':
        return render(request, url, context)

    form = UserForm(request.POST)

    # Validate the form
    if not form.is_valid():
        return render(request, url, context)

    new_user = User(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    is_active=False)

    new_user.save()

    key_length = 30
    random_key = ''.join(choice(ascii_uppercase) for i in range(key_length))

    buyer = Buyer()
    buyer.save()
    seller = Seller()
    seller.save()

    user_detail = UserDetail(user=new_user,
                            joined=timezone.now(),
                            bio="",
                            activation_key=random_key,
                            buyer=buyer,
                            seller=seller)
    user_detail.save()

    activation_url = 'http://localhost:8000/activate/' + random_key

    send_mail(subject="EventLite Verification",
              message="Go to {} to activate your EventLite account"
                      .format(activation_url),
              from_email="cgrabows@andrew.cmu.edu",
              recipient_list=[form.cleaned_data['email']])

    context = {"messages": ['An activation email has been sent.']}
    return render(request, 'index.html', context)


def view_events(request):
    return render(request, 'view-events.html', {})

# social login aftermath
# need to handle case where user hasn't activated account#
# Should be atomic
# 
def login_next(request):
    if(UserDetail.objects.filter(user=request.user).count()==0):
        print('no user exists')

        newProfile = UserDetail(user=request.user, joined=timezone.now())
        newProfile.save()
    else:
        print('user exists')
    return render(request, 'loggedin.html', {})
