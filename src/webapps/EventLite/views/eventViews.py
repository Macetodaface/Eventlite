from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, Http404, HttpResponse
from django.contrib.gis.geos import Point
from EventLite.models import *
from EventLite.forms import *
from sys import stderr

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


@login_required
def post_event(request):
    url = 'post-event.html'
    form = PostEventForm()

    if request.method == 'GET':
        return render(request, url, {'form': form})

    form = PostEventForm(request.POST)
    context = {'form': form}
    print(form)
    if not form.is_valid():
        return HttpResponse('Invalid Event Form',status=400)

    try:
        user_detail = UserDetail.objects.get(user=request.user)
        seller = user_detail.seller
    except:
        return HttpResponse('User Details Not found',status=400)

    #create Poin
    pointForm = PointForm(request.POST)
    if not pointForm.is_valid():
        return HttpResponse('Invalid Location Form',status=400)

    latitude = pointForm.cleaned_data['latitude']
    longitude = pointForm.cleaned_data['longitude']

    point = Point(float(longitude),float(latitude),srid=4326)

    new_event = Event.objects.create(seller=seller,
                name = form.cleaned_data['name'],
                description = form.cleaned_data['description'],
                location = form.cleaned_data['location'],
                time = form.cleaned_data['time'],
                media = form.cleaned_data['media'],
                email = form.cleaned_data['email'],
                coordinate=point
                )
    new_event.save()

    import json
    tickets = json.dumps(request.POST['tickets_data'])
    tickets = eval(json.loads(tickets))
    print(tickets)

    if not 'tickets_data' in request.POST:
        context['errors']=['No ticket data found']
        return render(request,url,context)

    print('ticket data present');


    for ticket in tickets:
        ticketTypeForm = TicketTypeForm(ticket)

        if not ticketTypeForm.is_valid():
            return HttpResponse('Invalid Ticket Type Form',status=400)

        ticketData = ticketTypeForm.cleaned_data

        ticket = TicketType.objects.create( name= ticketData['name'],
                                            event = new_event,
                                            price =ticketData['price'],
                                            details =ticketData['details'],
                                            numOfTickets =ticketData['numOfTickets']
        )
        ticket.save()

    context = my_events_context(request)
    context['messages'] = ['Your event has beeen posted']
    return HttpResponse()


@login_required
def ticket_type_html(request, id):
    context = {'id': id, 'form': TicketTypeForm()}
    return render(request, 'ticketType.html', context)


@login_required
def search_events(request):
    if request.method == 'GET':
        return view_events(request)

    if 'search' in request.POST and request.POST['search']:
        print(request.POST['search'])

        #Enable Full Text Search
        #vector = SearchVector('name', 'description')
        vector = SearchVector('name', weight='A') + SearchVector('description', weight='B')
        query = SearchQuery(str(request.POST['search']))
        events = Event.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.2).order_by('-rank')
        print(events)

        if not events:
            nameResult = Event.objects.filter(name__icontains=str(request.POST['search']))
            nameDesc = Event.objects.filter(description__icontains=str(request.POST['search']))
            print(nameResult)
            print(nameDesc)
            events = nameResult | nameDesc;
        #events = Event.objects.annotate(search=SearchVector('name','description')).filter(search=request.POST['search'])


        context = {'user': request.user,
                   'events': events}
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
