
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from string import ascii_uppercase
from random import choice
from EventLite.models import *
from EventLite.forms import *
from django.core.mail import send_mail

from django.contrib.auth import login, authenticate,logout
from django.db import transaction
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from sys import stderr

# Create your views here.


def index(request):
    context={}
    context['form'] = LoginForm()
    return render(request, 'index.html',context)



def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})

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

    new_user = User.objects.create(username=form.cleaned_data['username'],
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
    return render(request, 'index.html', context)

@login_required
def view_events(request):
    return render(request, 'view-events.html', {'user':request.user})

@login_required
def logoutUser(request):
    logout(request)
    return redirect('/')


def manual_login(request):
    if request.method == 'GET':
        return index(request)
    else:
        form = LoginForm(request.POST)
        if not form.is_valid():
            return index(request)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        print 'input UserName:' + username
        print 'input Password:' + password
        userdetail = UserDetail.objects.get(user__username=username)

        print 'stored UserName:'+userdetail.user.username
        print 'stored Password:'+userdetail.user.password

        print userdetail.user.is_active

        user = authenticate(username=username,password=password)
        if user is None:
            context={}
            context['form'] = LoginForm()
            return render(request, 'index.html',
              {'messages': ['User- None Invalid username/password.']})

        if user.is_active:
            if user is not None:
                login(request, user)
                return render(request, 'view-events.html', {})
        else:
            context['form'] = LoginForm()
            return render(request, 'index.html',
            {'messages': ['Account not activated. Check email to activate.']})


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
            # Ignore the activation key
            userDetail.user.is_active=True
            userDetail.user.save()
            userDetail.save()

    return render(request, 'view-events.html', {})

@transaction.atomic
def activate(request):
	if(request.method =='GET'):
		context={}
		if('key' not in request.GET or not request.GET['key'] ):
			context = {"messages": ['Invalid Activation Link']}
			return render(request,'index.html',context)
		link = request.GET['key']

        print link

        try:
			userdetail = UserDetail.objects.get(activation_key=link)
        except ObjectDoesNotExist:
            context = {"messages": ['Invalid Activation Link']}
            return render(request,'index.html',context)

        if(userdetail.user.is_active==True):
            context = {"messages": ['User already active']}
            return render(request,'index.html',context)

        userdetail.user.is_active=True
        userdetail.user.save();
        userdetail.activationLink=''
        userdetail.save();

        context = {"messages": ['User activation succeeded. Please login below']}
        return render(request,'index.html',context)



def recover_password(request):
    return render(request, 'recover-password.html', {})


def get_random_key():
    return ''.join(choice(ascii_uppercase) for i in range(30))


def new_password(request, key):
    context = {'key': key}
    print(key, file=stderr)
    try:
        user_detail = UserDetail.objects.get(recovery_key=key)
    except:
        return render(request, 'index.html', {'messages': ['Invalid Key']})
    if request.method == 'GET':
        return render(request, 'new_password.html', {})

    form = PasswordForm(request.POST)
    if form.is_valid():
        password = form.cleaned_data['password1']
        user = user_detail.user
        user.set_password(password)
        user.save()
    else:
        context['errors'] = form.errors
        return render(request, 'new_password.html', context)

    return render(request, 'index.html', {'mesasges':
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
