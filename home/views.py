from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginFormAuthentication
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.models import User
from django.conf import settings
import sweetify, urllib, json

# Create your views here.

def index(request):
    login_form = LoginFormAuthentication(request, data=request.POST)
    register_form = RegistrationForm(request.POST)
    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    
    return render(request, "home/index.html", context)

def loginForm(request):
    form = LoginFormAuthentication(request, data=request.POST)
    if form.is_valid():

        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        if result['success']:
            user = form.get_user()
            login(request, user)
            sweetify.toast(request, 'Succesfully logged in!', icon="success", timer=1000)
            return redirect("Home")
        else:
            sweetify.toast(request, 'Invalid reCAPTCHA. Please try again.', icon="error", timer=1000)
            return redirect("Home")
    else:
        if request.method == "POST":
            # get data from input fields username & password (Default fieldtext names django)
            username = request.POST.get("username")
            password = request.POST.get("password")
            # Authenticate user using django authenticate function
            user = authenticate(request, username=username, password=password)
            # If user does not exist (None) in database execute return function and display error message
            sweetify.toast(request, 'Invalid Username or Password!', icon="error", timer=2000)
            if user is None:
                return redirect("Home")
  
    return render(request, "home/login.html", {"form": form})

def registerForm(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            sweetify.toast(request, 'Username already exists! Please try again', icon="error", timer=3000)
            return redirect("Home")
        if form.is_valid():
            user = form.save()
            login(request, user)
            sweetify.toast(request, 'Succesfully registered!', icon="success", timer=1000)
            return redirect("Home")
        else:
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            if password1 != password2:
                sweetify.toast(request, 'Your passwords do not match or is Invalid!', icon="error", timer=2000)
                return redirect("Home")
            form = RegistrationForm()
           
    form = RegistrationForm()
    return render(request, "home/register.html", {"form": form})

def logout_request(request):
    logout(request)
    sweetify.toast(request, 'Succesfully logged out!', icon="success", timer=2500)
    return redirect("/")

def admin_panel(request):
    return redirect("admin/")