from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from . import forms
from . import models
from django.contrib.auth.models import User
from django.contrib import messages
# Create your views here.


def register(request):
    if request.method == "POST":    
        form = forms.CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successed, login to continue.')
            return redirect("user-login")
    else:
        form = forms.CreateUserForm()
    context = {
        'form' : form,
    }
    return render(request, 'user/register.html', context)



def profile(request, pk):
    return render(request, 'user/profile.html')



def profile_update(request, pk):
    if request.method == "POST":
        user_form = forms.UserUpdateForm(request.POST , instance=request.user)
        profile_form = forms.ProfileUpdateForm(request.POST , instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("user-profile", pk=request.user.id)
    else:
        user_form = forms.UserUpdateForm(instance=request.user)
        profile_form = forms.ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form' : user_form,
        'profile_form' : profile_form,

    }
    return render(request, 'user/profile_update.html', context)

