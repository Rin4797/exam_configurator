from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from django.shortcuts import  render, redirect

from django.contrib.auth import login
from django.contrib import messages

def register_request(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("/")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = UserCreationForm()
	return render (request=request, template_name="registration/register.html", context={"register_form":form})
