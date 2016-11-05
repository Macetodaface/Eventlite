
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import transaction
from string import ascii_uppercase
from random import choice
from EventLite.models import *
from EventLite.forms import *
from django.core.mail import send_mail

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
        newProfile = UserDetail(user=request.user,buyer=newBuyer,seller=newSeller, joined=timezone.now())

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
