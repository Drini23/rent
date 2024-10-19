from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, request
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.
def home(request):
    return render(request, 'authentication/index.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        messages.success(request, "Your Account has been successfully created.")
        return redirect('signin')

    return render(request, 'authentication/singup.html')


def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, f"Welcome {fname}!")
            return redirect('qera:home')  # Assuming 'home' is the name of the URL for the home page
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('signin')

    return render(request, 'authentication/singin.html')


def singout(request):
    logout(request)
    messages.success(request, "Logged out Successfuly!")
    return redirect('home')
