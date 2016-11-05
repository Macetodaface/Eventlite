from django import forms
from django.forms import ModelForm
from EventLite.models import *


class PostEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['description', 'location', 'time', 'media', 'email']


class UserForm(forms.Form):
    username = forms.CharField(max_length=40, label='Username')
    first_name = forms.CharField(max_length=40, label='First Name')
    last_name = forms.CharField(max_length=40, label='Last Name')
    email = forms.CharField(max_length=40, label='Email')
    password1 = forms.CharField(max_length=40, label='Password:',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=40, label='Confirm Password:',
                                widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError('Username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError('Email is already taken.')
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1 == password2:
            raise forms.ValidationError('Passwords do not match.')
        return password1

class LoginForm(forms.Form):
    username = forms.CharField(max_length=40, label='Username')
    password = forms.CharField(max_length=40, label='Password:',
                                widget=forms.PasswordInput)
    def clean(self):
        cleaned_data= super(LoginForm,self).clean()
        return cleaned_data
