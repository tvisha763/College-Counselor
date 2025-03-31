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
        user = User.objects.get(email=request.session["email"])
        context = {
            'user' : user,
        }
        if request.method == "POST":
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            email = request.POST.get('email')
            grade = request.POST.get('grade')
            location = request.POST.get('location')
            citizenship = request.POST.get('citizenship')
            first_gen = request.POST.get('first_gen')
            ethnicity = request.POST.get('ethnicity')
            gender = request.POST.get('gender')
            college_goals = request.POST.get('college_goals')
            major_goals = request.POST.get('major_goals')
            resume = request.FILES.get('resume')
            class_rank = request.POST.get('class_rank')
            class_size = request.POST.get('class_size')
            psat = request.POST.get('psat')
            sat = request.POST.get('sat')
            act = request.POST.get('act')
            school = request.POST.get('school')

            inputs = [fname, lname, email, grade, location, citizenship, first_gen, ethnicity, gender, college_goals, major_goals, resume, class_rank, class_size, psat, sat, act, school]

            for i in range(len(inputs)):
                if inputs[i] == "":
                    inputs[i] = None               

            user.fname = inputs[0]
            user.lname = inputs[1]
            user.email = inputs[2]
            user.grade = inputs[3]
            user.location = inputs[4]
            user.citizenship_status = inputs[5]
            user.first_gen = inputs[6]
            user.ethnicity = inputs[7]
            user.gender = inputs[8]
            user.college_goals = inputs[9]
            user.major_goals = inputs[10]
            user.resume = inputs[11]
            user.class_rank = inputs[12]
            user.class_size = inputs[13]
            user.psat = inputs[14]
            user.sat = inputs[15]
            user.act = inputs[16]
            user.school = inputs[17]
            user.save()

        
        return render(request, "edit_profile.html", context)