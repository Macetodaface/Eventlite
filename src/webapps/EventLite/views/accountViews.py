from django.shortcuts import render,redirect
from django.db import transaction
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

from EventLite.models import *
from EventLite.forms import *

from string import ascii_uppercase
from random import choice

from django.contrib.auth import  login,authenticate,logout

def index(request, context):
    context['form'] = LoginForm()
    return render(request, 'index.html', context)

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
            context['messages'] = ['Invalid UserName or Password']
            return index(request, context)

        user = authenticate(username=username,password=password)

        if user is None:
            if storedUser.is_active:
                context['messages'] = ['Invalid UserName or Password']
                return index(request,context)
            else:
                context['messages'] = ['Account not activated. Check email to activate.']
                return index(request, context)
        login(request,user)
        return redirect('/view-events')


@transaction.atomic
def social_login(request):
    if(UserDetail.objects.filter(user__email=request.user.email).count()==0):
        newBuyer = Buyer()
        newSeller = Seller()
        newBuyer.save()
        newSeller.save()
        newProfile = UserDetail(user=request.user,buyer=newBuyer,seller=newSeller, joined=timezone.now())
        newProfile.save()
    else:
        # check activation
        userDetail = UserDetail.objects.get(user__email=request.user.email)
        if(userDetail.user.is_active==False):
            context = {"messages": ['Cant use social login while user email activation pending']}
            return index(request,context)

    return redirect('/view-events')


@transaction.atomic
def activate(request):
    if(request.method =='GET'):
        context={}
        if('key' not in request.GET or not request.GET['key'] ):
            context = {"messages": ['Invalid Activation Link']}
            return index(request,context)
        link = request.GET['key']

        try:
            userdetail = UserDetail.objects.get(activation_key=link)
        except ObjectDoesNotExist:
            context = {"messages": ['Invalid Activation Link']}
            return index(request,context)

        if(userdetail.user.is_active==True):
            context = {"messages": ['User already active']}
            return index(request,context)

        userdetail.user.is_active=True
        userdetail.user.save()
        userdetail.activationLink=''
        userdetail.save()

        context = {"messages": ['User activation succeeded. Please login below']}
        return index(request,context)

def getRandomKey():
    key_length = 30
    return ''.join(choice(ascii_uppercase) for i in range(key_length))


@login_required()
def profile(request):
    return render(request, 'profile.html', {})

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

        random_key = getRandomKey()
        while UserDetail.objects.filter(recovery_key=random_key).count() > 0:
            random_key = getRandomKey()

        user_detail.recovery_key = random_key
        user_detail.save()
        reset_url = 'localhost:8000/new_password/' + random_key
        send_mail(subject="EventLite Password reset",
                  message="Go to {} to reset your password".format(reset_url),
                  from_email="noreply@EventLite.com",
                  recipient_list=[user.email])

        context = {'messages': ['An email has been sent ' +
                                'with instructions to ' +
                                'reset your password']}
        return index(request,context)

def new_password(request, key):
    context = {'key': key}

    if request.method == 'GET':
        return render(request, 'new_password.html', context)

    form = PasswordForm(request.POST)
    if form.is_valid():
        password = form.cleaned_data['password1']
        try:
            user_detail = UserDetail.objects.get(recovery_key=key)
        except:
            return index(request,{'messages': ['Invalid Key']})
        user = user_detail.user
        user.set_password(password)
        user.save()
    else:
        context['form'] = form
        return render(request, 'new_password.html', context)

    context['messages'] = ['Your password has been reset']
    return index(request,context)


@login_required
def logoutUser(request):
    auth_logout(request)
    return redirect('/')
