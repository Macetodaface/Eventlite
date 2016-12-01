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
import json
import requests

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.shortcuts import get_object_or_404
from mimetypes import guess_type
from datetime import datetime
from django.utils import timezone


@login_required
def post_event(request):
    url = 'post-event.html'
    form = PostEventForm()

    if request.method == 'GET':
        return render(request, url, {'form': form})


    print(request)
    print(request.POST)
    print(request.FILES)

    form = PostEventForm(request.POST)
    context = {'form': form}
    if not form.is_valid():
        return HttpResponse('Invalid Event Form',status=400)

    try:
        user_detail = UserDetail.objects.get(user=request.user)
        seller = user_detail.seller
    except:
        return HttpResponse('User Details Not found',status=400)

    #create Point
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

    if(request.FILES and 'seatLayout' in request.FILES):
        print("seat Layour saved")
        new_event.seatLayout=request.FILES['seatLayout']
        new_event.save()


    tickets = json.dumps(request.POST['tickets_data'])
    tickets = eval(json.loads(tickets))


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

    events = Event.objects.all()


    if 'search' in request.POST and request.POST['search']:

        print(request.POST['search'])

        #Enable Full Text Search
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

    #Add Filters
    # Location
    if 'location' in request.POST and request.POST['location']:

        # gonna contain latitude and longitude
        location = request.POST['location']
        dict = getLatLong(location)
        print (dict)
        if(dict['result'] == 'not ok'):
            context={'errors':'Invalid Location specified'}
            return view_events(request)

        latitude = dict['lat']
        longitude = dict['long']

        # miles
        miles = 20
        if 'radius' in request.POST and request.POST['radius']:
            miles = int(request.POST['radius'])

        if(miles<0):
            context={'errors':'Enter Valid Miles'}
            return view_events(request)

        point = Point(longitude,latitude,srid=4326)
        events = events.filter(coordinate__distance_lte=(point,D(mi=miles)))


    context = {
                'user': request.user,
                'events': events
               }

    return render(request, 'view-events.html', context)



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
    buyer = user_detail.buyer
    tickets = buyer.ticket_set.all()
    events_attending = Event.objects.none()
    past_events =  Event.objects.none()

    #fiter out future events
    for ticket in tickets:
        events_attending = events_attending | Event.objects.filter(id=ticket.ticketType.event.id)
        past_events = events_attending
        events_attending = events_attending & Event.objects.filter(time__gte=datetime.now())

    #only contains future events
    hosted_events = Event.objects.filter(seller=seller)
    past_events =  past_events | hosted_events
    hosted_events = hosted_events & Event.objects.filter(time__gte=datetime.now())


    past_events = past_events.filter(time__lte=datetime.now()).order_by('time').reverse()

    context = {'user': request.user,
               'events_hosting': hosted_events.order_by('time'),
               'events_attending': events_attending.order_by('time'),
               'past_events':past_events}
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
            return event_page(request, id)
        else:
            return event_page(request, id)



@login_required
@transaction.atomic
def buy_ticket(request, id):
    url = 'event.html'
    try:
        ticket_type = TicketType.objects.get(id=id)
    except:
        raise Http404


    event_id = ticket_type.event.id
    context = get_event_page_context(event_id)
    if request.method == 'POST':
        form = BuyTicketsForm(request.POST)
        context['form'] = form

        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            print(ticket_type.ticketsSold, file=stderr)
            tickets_left = ticket_type.numOfTickets - ticket_type.ticketsSold
            if quantity > tickets_left:
                context['errors'] = "Not enough tickets available."
                return render(request, url, context)
            try:
                user_detail = UserDetail.objects.get(user=request.user)
                buyer = user_detail.buyer
                try:
                    tickets = buyer.ticket_set.all()
                    ticket = tickets.filter(ticketType__id=ticket_type.id)[0]
                    ticket.quantity += quantity
                except:
                    ticket = Ticket.objects.create(buyer=buyer,
                                                   ticketType=ticket_type,
                                                   quantity=quantity)
                finally:
                    ticket_type.ticketsSold += quantity
                    ticket_type.save()
                    ticket.save()
            except:
                context['errors'] = ['User details not found.']
                return render(request, url, context)
        else:
            return render(request, url, context)
    return event_page(request, event_id)


def get_event_page_context(id):
    context = {'form': BuyTicketsForm()}
    try:
        event = Event.objects.get(id=id)
    except:
        context['errors'] = ['No event found.']
        return context
    seller = event.seller
    try:
        user_detail = UserDetail.objects.get(seller=seller)
    except:
        context['errors'] = ['User details not found.']
        return context

    date = timezone.now()

    if(event.time > date):
        context['reviews'] = False

    else:
        context['reviews'] = True
        context['form'] = ReviewForm()

    context['event'] = event
    context['seller_username'] = user_detail.user.username
    context['ticketTypes'] = event.tickettype_set.all()
    context['userTickets'] = user_detail.buyer.ticket_set.all()
    context['reviews'] = Review.objects.filter(event_id=id)

    return context

@login_required
def event_page(request, id):
    url = 'event.html'
    context = get_event_page_context(id)
    return render(request, url, context)


@login_required
@transaction.atomic
def add_review(request,id):
    if request.method == 'POST':
        url = 'event.html'
        form = ReviewForm(request.POST)

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

        context ={}
        if not form.is_valid():

            context['errors'] = ['Add Review Error']
            print("Invalid form!")
            context = get_event_page_context(id)
            context['form'] = form
            return render(request, url, context)

        review = Review.objects.create( rating=form.cleaned_data['rating'],
                                        review = form.cleaned_data['review'],
                                        event = event ,
                                        reviewer = user_detail)
        review.save()
        print("review saved!")
        return event_page(request, id)


def getLatLong(location):
    address = location
    api_key = "AIzaSyAGAfMw23ko_z5TJLg_nfi6PLClCxQ7yqw"
    api_response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address, api_key))
    api_response_dict = api_response.json()

    if api_response_dict['status'] == 'OK':
        latitude = api_response_dict['results'][0]['geometry']['location']['lat']
        longitude = api_response_dict['results'][0]['geometry']['location']['lng']

        print( 'Latitude:', latitude)
        print ('Longitude:', longitude)
        return {'result':'ok','lat':float(latitude), 'long':float(longitude)}

    return {'result':'not ok'}



@login_required
def getSeatLayout(request,id):
	event = get_object_or_404(Event,id=id)

	if not event.seatLayout:
		raise Http404

	contentType = guess_type(event.seatLayout.name)
	return HttpResponse(event.seatLayout,content_type=contentType)
