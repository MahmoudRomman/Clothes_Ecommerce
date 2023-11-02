from django import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        required = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']



class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        required = ['username', 'first_name', 'last_name', 'email']

        
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ['phone']