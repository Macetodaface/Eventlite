from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    seller = models.OneToOneField("Seller", blank=True)
    buyer = models.OneToOneField("Buyer", blank=True)
    icon = models.ImageField(upload_to='icons', blank=True)
    bio = models.CharField(max_length=420, default='', blank=True)
    email = models.EmailField()
    social_login = models.BooleanField()


class Seller(models.Model):
    eventsHosting = models.ForeignKey("Event", blank=True)


class Buyer(models.Model):
    eventsInterested = models.ForeignKey("Event", blank=True)
    ticketsPurchased = models.ForeignKey("Ticket", blank=True)
    points = models.IntegerField(default=0)


class Event(models.Model):
    numOfTickets = models.IntegerField(default=0)
    ticketsSold = models.IntegerField(default=0)
    description = models.CharField(max_length=1000, default='', blank=True)
    location = models.CharField(max_length=100, default='', blank=True)
    time = models.DateTimeField(default=timezone.now)
    media = models.URLField(default='', blank=True)
    email = models.EmailField()


class Ticket(models.Model):
    event = models.ForeignKey("Event")
    price = models.FloatField()
    details = models.CharField(max_length=1000)


class Review(models.Model):
    rating=models.IntegerField()
    review=models.CharField(max_length=420, default='', blank=True)
    event=models.ForeignKey("Event")


class Image(models.Model):
    event=models.ForeignKey("Event")
    image=models.ImageField(upload_to='images', blank=True)