from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserDetail(models.Model):
     user = models.OneToOneField(User, on_delete = models.CASCADE)
     seller = models.OneToOneField("Seller", blank=True,null=True)
     buyer = models.OneToOneField("Buyer", blank=True,null=True)
     icon = models.ImageField(upload_to = 'icons', blank = True,null=True)
     bio = models.CharField(max_length = 420, default = '', blank = True,null=True)
     joined = models.DateTimeField()
     activation_key = models.CharField(max_length=100)
     recovery_key = models.CharField(max_length=100, blank=True)

class Seller(models.Model):
    earnings = models.FloatField(default=0.0)

class Buyer(models.Model):
    ticketsPurchased = models.ManyToManyField("Ticket", blank=True)
    eventsInterested = models.ManyToManyField("Event", blank=True)
    points = models.IntegerField(default = 0)

class Event(models.Model):
	seller = models.ForeignKey(Seller)
	description = models.CharField(max_length = 1000, default = '', blank = True)
	location = models.CharField(max_length = 100, default = '', blank = True)
	time = models.DateTimeField(default=timezone.now)
	media = models.URLField(default = '', blank = True)
	email = models.EmailField()


class Ticket(models.Model):
    event = models.ForeignKey(Event)
    price = models.FloatField()
    details = models.CharField(max_length=1000)
    numOfTickets = models.IntegerField(default=0)
    ticketsSold = models.IntegerField(default=0)


class Review(models.Model):
    rating = models.IntegerField()
    review = models.CharField(max_length = 420, default = '', blank = True)
    event = models.ForeignKey(Event)

class Image(models.Model):
    event = models.ForeignKey(Event)
    image = models.ImageField(upload_to = 'images', blank = True)
