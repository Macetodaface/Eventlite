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
    if (UserDetail.objects.filter(user=request.user).count() == 0):
        print('no user exists')

        newProfile = UserDetail(user=request.user,social_login=True)
        newProfile.save()
    else:
        print('user exists')
    return render(request, 'loggedin.html', {})


def recover_password(request):
    return render(request, 'recover-password.html', {})


def get_random_key():
    return ''.join(choice(ascii_uppercase) for i in range(30))


def new_password(request, key):
    try:
        user_detail = UserDetail.objects.get(reset_key=key)
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
        return render(request, 'new_password.html', {'errors':forms.errors})

    return render(request, 'index.html', {'mesasges':
                                    ['Your password has been reset']})


def recover_password(request):
    if request.method == 'GET':
        return render(request, 'recover-password.html', {})

    form = RecoveryForm(request.POST)

    if not form.is_valid():
        return render(request, 'recover-password.html', {'errors': form.non_field_errors()})

    else:
        user = form.get_user()
        try:
            user_detail = UserDetail.objects.get(user=user)
        except:
            return render(request, 'recover-password.html', {'errors': 'Cannot find user details.'})

        random_key = get_random_key()
        while UserDetail.objects.filter(recovery_key=random_key).size() > 0:
            random_key = get_random_key()

        user_detail.recovery_key = random_key
        user_detail.save()
        reset_url = 'localhost:8000/new_password/' + random_key
        send_mail(subject="EventLite Password reset",
                  message="Go to {} to reset your password".format(reset_url),
                  from_email="noreply@EventLite.com",
                  recipient_list=[user.email])
    return render(request, 'index.html', {'messages': ['An email has been sent' +
                                                       'with instructions to ' +
                                                       'reset your password']})