from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, Http404, HttpResponse

from EventLite.models import *
from EventLite.forms import *

from sys import stderr


@login_required
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
                name = form.cleaned_data['name'],
                description = form.cleaned_data['description'],
                location = form.cleaned_data['location'],
                time = form.cleaned_data['time'],
                media = form.cleaned_data['media'],
                email = form.cleaned_data['email'])
    new_event.save()
    context = my_events_context(request)
    context['messages'] = ['Your event has beeen posted']
    return render(request, 'my-events.html',context)





@login_required
def search_events(request):
    if request.method == 'GET':
        return view_events(request)

    if 'search' in request.POST and request.POST['search']:
        print(request.POST['search'])
        context = {'user': request.user,
                   'events': Event.objects.filter(name=request.POST['search'])}
        return render(request, 'view-events.html', context)

    else:
        return view_events(request)


@login_required
def view_events(request):
    context = {'user': request.user,
               'events': Event.objects.all()}
    return render(request, 'view-events.html', context)


@login_required
def my_events_context(request):
    try:
        user_detail = UserDetail.objects.get(user=request.user)
    except:
        return {'errors': 'Could not find user details.'}

    seller = user_detail.seller
    context = {'user': request.user,
               'events': Event.objects.filter(seller=seller)}
    return context


@login_required
def my_events(request):
    return render(request, 'my-events.html', my_events_context(request))



@login_required
def event_info(request,id):

    if request.method == "GET":
        #see if the user is the host of the event
        try:
            user_detail = UserDetail.objects.get(user=request.user)
        except:
            #user doesn't exist
            raise Http404

        try:
            event = Event.objects.get(id=id)
        except:
            #event doesn't exist
            raise Http404

        #if yes, redirect to seller- event views
        if(event.seller == user_detail.seller):
            return event_page(request,id)
        else:
            return event_page(request,id)

@login_required
def event_page(request, id):
    url='event.html'
    context = {}
    try:
        event = Event.objects.get(id=id)
    except:
        context['errors'] = ['No event found.']
        return render(request, url, context)
    seller = event.seller
    try:
        user_detail = UserDetail.objects.get(seller=seller)
    except:
        context['errors'] = ['User details not found.']
        return render(request, url, context)

    context['event']= event
    context['seller_username'] = user_detail.user.username
    return render(request, url, context)
