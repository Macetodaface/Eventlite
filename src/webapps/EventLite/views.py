from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'index.html', {})


def base(request):
    return render(request, 'base.html', {})


def post_event(request):
    return render(request, 'post-event.html', {})


def registration(request):
    return render(request, 'registration.html', {})


def login_next(request):
    return render(request, 'loggedin.html', {})
