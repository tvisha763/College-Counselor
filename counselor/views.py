from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Course, Schedule, TakenCourse, Extracurricular, Award, Message, TakenEC, WonAward, EssayDraft, College, CollegeApplication, Scholarship
import bcrypt
import requests
import urllib
import os
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.


def home(request):
    return render(request, "home.html")

def signup(request):
    if not request.session.get('logged_in') or not request.session.get('email'):
        if request.method == "POST":

            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            password = request.POST.get('password').encode("utf8")
            confirmPass = request.POST.get('confirmPass').encode("utf8")
            
            inputs = [fname, lname, email, password, confirmPass]

            if (password != confirmPass):
                messages.error(request, "The passwords do not match.")
                return redirect('signup')

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('signup')

            if password != '' and len(password) < 6:
                messages.error(request, "Your password must be at least 6 charecters.")
                return redirect('signup')

            if "@" not in email:
                messages.error(request, "Please enter your email address.")
                return redirect('signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. If this is you, please log in.")
                return redirect('signup')

            else:
                salt = bcrypt.gensalt()
                user = User()
                user.email = email
                user.fname = fname
                user.lname = lname
                user.password = bcrypt.hashpw(password, salt)
                user.salt = salt
                user.save()
                user = User.objects.get(email=email)
                return redirect('login')
        else:
            if request.session.get('logged_in'):
                return redirect('/login')
    else:
        return redirect('dashboard')

    return render(request, 'auth/signup.html')


def login(request):
    if not request.session.get('logged_in') or not request.session.get('email'):
        if request.method == "POST":
            email = request.POST.get('email')
            password = request.POST.get('password').encode("utf8")
            inputs = [email, password]

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('login')

            

            if User.objects.filter(email=email).exists():
                saved_hashed_pass = User.objects.filter(email=email).get().password.encode("utf8")[2:-1]
                saved_salt = User.objects.filter(email=email).get().salt.encode("utf8")[2:-1]
                user  = User.objects.filter(email=email).get()
                request.session["email"] = user.email
                request.session['logged_in'] = True
            
                salted_password = bcrypt.hashpw(password, saved_salt)
                if salted_password == saved_hashed_pass:
                    return redirect('dashboard')
                else:
                    messages.error(request, "Your password is incorrect.")
                    return redirect('login')

            else:
                messages.error(request, "An account with this email does not exist. Please sign up.")
                return redirect('login')

        else:
            if request.session.get('logged_in'):
                return redirect('/login')

        return render(request, 'auth/login.html')
    else:
        return redirect('dashboard')

def logout(request):
    if not request.session.get('logged_in') or not request.session.get('email'):
        return redirect('/login')
    else:
        request.session["email"] = None
        request.session['logged_in'] = False
        return redirect('/')



def home(request):
        return render(request, 'home.html')

def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        return render(request, "dashboard.html")
    
def edit_profile(request):
    if not request.session.get('logged_in'):
        return redirect('/login')
    else:
        return render(request, "edit_profile.html")