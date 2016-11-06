
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from string import ascii_uppercase
from random import choice
from EventLite.models import *
from EventLite.forms import *
from django.core.mail import send_mail

from django.contrib.auth import  login,authenticate,logout
from django.db import transaction
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from sys import stderr
from django.contrib.auth import logout as auth_logout

# Create your views here.


def index(request, context):
    context['form'] = LoginForm()
    return render(request, 'index.html',context)


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    url = 'post-event.html'
    form = PostEventForm()
    if request.method == 'GET':
        return render(request, url, {'form': form})

    form = PostEventForm(request.POST)
    context = {'form': form}
    if not form.is_valid():
        return render(request, url, context)

    try:
        user_detail = UserDetail.objects.get(user=request.user)
        seller = user_detail.seller
    except:
        context['errors'] = ['User details not found.']
        return render(request, url, context)

    new_event = Event.objects.create(seller=seller,
                description = form.cleaned_data['description'],
                location = form.cleaned_data['location'],
                time = form.cleaned_data['time'],
                media = form.cleaned_data['media'],
                email = form.cleaned_data['email'])
    new_event.save()
    return render(request, 'view-events.html',
                  {'messages': ['Your event has been posted.']})

def getRandomKey():
    key_length = 30
    return ''.join(choice(ascii_uppercase) for i in range(key_length))

@transaction.atomic
def registration(request):
    url = 'registration.html'
    context = {}

    if request.method == 'GET':
        return render(request, url, context)

    form = UserForm(request.POST)
    context['form'] = form

    # Validate the form
    if not form.is_valid():
        return render(request, url, context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    is_active=False)

    new_user.save()

    random_key = getRandomKey()

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

    activation_url = "http://localhost:8000/activate?key=" +random_key

    send_mail(subject="EventLite Verification",
              message="Go to {} to activate your EventLite account"
              .format(activation_url),
              from_email="noreply@EventLite.com",
              recipient_list=[form.cleaned_data['email']])

    context = {"messages": ['An activation email has been sent.']}
    return index(request, context)

@login_required
def view_events(request):
    return render(request, 'view-events.html', {'user':request.user})

@login_required
def logoutUser(request):
    auth_logout(request)
    return redirect('/')


def manual_login(request):
    if request.method == 'GET':
        return index(request, {})
    else:
        context={}
        form = LoginForm(request.POST)
        if not form.is_valid():
            return index(request, {})

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        try:
            storedUser = User.objects.get(username=username)
        except:
            print 'inside storedUser'
            context['messages'] = ['Invalid UserName or Password']
            return index(request,context)

        user = authenticate(username=username,password=password)


        if user is None:
            if storedUser.is_active:
                context['messages'] = ['Invalid UserName or Password']
                return index(request,context)
            else:
                context['messages'] = ['Account not activated. Check email to activate.']
                return render(request, 'index.html',context)


# social login aftermath
# need to handle case where user hasn't activated account#
# Should be atomic
@transaction.atomic
def social_login(request):
    if(UserDetail.objects.filter(user__email=request.user.email).count()==0):
        print('user inactive- social login')
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
        if(userDetail.user.is_active==False):
            print('user inactive- social login')
            context = {"messages": ['Cant use social login while user email activation pending']}
            return render(request,'index.html',context)

    return redirect('/view-events')

@transaction.atomic
def activate(request):
    if(request.method =='GET'):
        context={}
        if('key' not in request.GET or not request.GET['key'] ):
            context = {"messages": ['Invalid Activation Link']}
            return render(request,'index.html',context)
        link = request.GET['key']

        try:
            userdetail = UserDetail.objects.get(activation_key=link)
        except ObjectDoesNotExist:
            context = {"messages": ['Invalid Activation Link']}
            return render(request,'index.html',context)

        if(userdetail.user.is_active==True):
            context = {"messages": ['User already active']}
            return render(request,'index.html',context)

        userdetail.user.is_active=True
        userdetail.user.save()
        userdetail.activationLink=''
        userdetail.save()

        context = {"messages": ['User activation succeeded. Please login below']}
        return render(request,'index.html',context)



def recover_password(request):
    return render(request, 'recover-password.html', {})


def get_random_key():
    return ''.join(choice(ascii_uppercase) for i in range(30))


def new_password(request, key):
    context = {'key': key}

    try:
        user_detail = UserDetail.objects.get(recovery_key=key)
    except:
        return render(request, 'index.html', {'messages': ['Invalid Key']})

    if request.method == 'GET':
        return render(request, 'new_password.html', context)

    form = PasswordForm(request.POST)
    if form.is_valid():
        password = form.cleaned_data['password1']
        try:
            user_detail = UserDetail.objects.get(recovery_key=key)
        except:
            return render(request, 'index.html', {'messages': ['Invalid Key']})
        user = user_detail.user
        user.set_password(password)
        user.save()
    else:
        context['errors'] = form.errors
        return render(request, 'new_password.html', context)

    return render(request, 'index.html', {'messages':
                                    ['Your password has been reset']})


def recover_password(request):
    if request.method == 'GET':
        return render(request, 'recover-password.html', {})

    form = RecoveryForm(request.POST)

    context = {'form': form}
    if not form.is_valid():
        return render(request, 'recover-password.html', context)

    else:
        user = form.get_user()
        try:
            user_detail = UserDetail.objects.get(user=user)
        except:
            return render(request, 'recover-password.html', {'errors': 'Cannot find user details.'})

        random_key = get_random_key()
        while UserDetail.objects.filter(recovery_key=random_key).count() > 0:
            random_key = get_random_key()

        user_detail.recovery_key = random_key
        user_detail.save()
        reset_url = 'localhost:8000/new_password/' + random_key
        send_mail(subject="EventLite Password reset",
                  message="Go to {} to reset your password".format(reset_url),
                  from_email="noreply@EventLite.com",
                  recipient_list=[user.email])
        return render(request, 'index.html', {'messages': ['An email has been sent ' +
                                                       'with instructions to ' +
                                                       'reset your password']})
