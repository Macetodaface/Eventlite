
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, Http404,HttpResponse

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
