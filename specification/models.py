from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserDetail(models.Model):
     user = models.OneToOneField(User, on_delete = models.CASCADE)
     seller = models.OneToOneField(Seller, blank=True)
     buyer = models.OneToOneField(Buyer, blank=True)
     isSeller = models.BooleanField(default = False)
     isBuyer = models.BooleanField(default = True)
     icon = models.ImageField(upload_to = 'icons', blank = True)
     bio = models.CharField(max_length = 420, default = '', blank = True)
     email = models.EmailField()

class Seller(models.Model):
    eventsHosting = models.ForeignKey(Event)

class Buyer(models.Model):
    eventsInterested = models.ForeignKey(Event)
    ticketsPurchased = models.ForeignKey(Ticket)
    points = models.IntegerField(default = 0)

class Event(models.Model):
    review = models.ForeignKey(Review)
    tickets = models.ForeignKey(Ticket)
    numOfTickets = models.IntegerField(default = 0)
    ticketsSold = models.IntegerField(default = 0)
    description = models.CharField(max_length = 1000, default = '', blank = True)
    location = models.CharField(max_length = 100, default = '', blank = True)
    time = models.DateTimeField(default=timezone.now)
    media = models.URLField(default = '', blank = True)
    images = models.ForeignKey(Image)
    email = models.EmailField()

class Ticket(models.Model):
    price = models.FloatField()

class Review(models.Model):
    review = models.CharField(max_length = 420, default = '', blank = True)

class Image(models.Model):
    image = models.ImageField(upload_to = 'images', blank = True)