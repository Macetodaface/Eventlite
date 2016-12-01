from django import forms
from django.forms import ModelForm
from EventLite.models import *
from sys import stderr


class BioForm(forms.Form):
    content = forms.CharField(max_length=420, label='Bio', required = False)


class ImageForm(forms.Form):
    image = forms.ImageField(required = False)


class PostEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'time', 'media',
                  'email','seatLayout','bannerImage']


class UserForm(forms.Form):
    username = forms.CharField(max_length=40, label='Username')
    first_name = forms.CharField(max_length=40, label='First Name')
    last_name = forms.CharField(max_length=40, label='Last Name')
    email = forms.CharField(max_length=40, label='Email',
                                widget=forms.EmailInput)
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

    def clean(self):
        cleaned_data=super(UserForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=40, label='Username')
    password = forms.CharField(max_length=40, label='Password:',
                                widget=forms.PasswordInput)
    def clean(self):
        cleaned_data= super(LoginForm,self).clean()
        return cleaned_data




class RecoveryForm(forms.Form):
    username = forms.CharField(max_length=100, required=False)
    email = forms.CharField(max_length=100, required=False)

    def get_user(self):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        if username:
            try:
                user = User.objects.get(username=username)
                return user
            except:
                raise forms.ValidationError('No user found for given username.')

        elif email:
            try:
                user = User.objects.get(email=email)
                return user
            except:
                raise forms.ValidationError('No user found for given email.')
        raise forms.ValidationError('Please enter a username or email address.')

    def clean(self):
        if not self.get_user():
            raise forms.ValidationError('No user found')
        return super(RecoveryForm, self).clean()


class PasswordForm(forms.Form):
    password1 = forms.CharField(max_length=40, label='Password:',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=40, label='Confirm Password:',
                                widget=forms.PasswordInput)

    def clean(self):
        cleaned_data=super(PasswordForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

class PointForm(forms.Form):
    latitude = forms.DecimalField()
    longitude = forms.DecimalField()

class TicketTypeForm(ModelForm):
    class Meta:
        model = TicketType
        fields = ['name', 'price', 'details', 'numOfTickets']

class BuyTicketsForm(forms.Form):
    quantity = forms.IntegerField()

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating','review']
        widgets ={
            'review': forms.Textarea(attrs={'rows':'4','cols':'400','placeholder':'Enter a Review (420 char max)','class':'form-control'})

        }
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')

        if(type(rating) != int):
            raise forms.ValidationError("Enter an integer between 1 and 5!")
        if(rating<1 or rating>5):
            raise forms.ValidationError('Enter an integer between 1 and 5')

        return rating

    def clean_review(self):
        review = self.cleaned_data.get('review');

        if(len(str(review))<10):
            raise forms.ValidationError("Review should be atleast 10 characters")

        return review
