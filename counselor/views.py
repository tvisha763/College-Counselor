from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import bcrypt
import requests
import urllib
import os
import json
from datetime import date
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login as auth_login

# MAKE SURE TO USE THESE?
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .utils import (
    GRADE_SCHEDULE_FIELDS,
    get_or_create_course,
    update_schedule_entry,
    serialize_schedule,
    serialize_extracurriculars,
)

def home(request):
    return render(request, "home.html")

def signup(request):
    if request.method == "POST":
        fname = request.POST.get('fname', '').strip()
        lname = request.POST.get('lname', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_pass = request.POST.get('confirmPass', '')

        if not all([fname, lname, email, password, confirm_pass]):
            messages.error(request, "Please fill in all fields.")
            return redirect('counselor:signup')

        if password != confirm_pass:
            messages.error(request, "Passwords do not match.")
            return redirect('counselor:signup')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('counselor:signup')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect('counselor:signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please log in.")
            return redirect('counselor:signup')

        user = User(email=email, fname=fname, lname=lname)
        user.set_password(password)

        schedule_refs = {}
        for grade, label in [(9, "freshman_schedule"), (10, "sophomore_schedule"),
                             (11, "junior_schedule"), (12, "senior_schedule")]:
            schedule = Schedule.objects.create(
                id_phrase=f"{email}_{label.split('_')[0]}",
                grade=grade,
                grades=json.dumps({"sem1": {}, "sem2": {}}),
                ap_scores=json.dumps({}),
                ib_scores=json.dumps({})
            )
            schedule_refs[label] = schedule

        for field_name, schedule in schedule_refs.items():
            setattr(user, field_name, schedule)

        user.save()

        messages.success(request, "Account created successfully. Please log in.")
        return redirect('counselor:login')

    return render(request, 'auth/signup.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('counselor:dashboard')
    
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Please input all the information.")
            return redirect('counselor:login')

        user = authenticate(request, email=email, password=password)
        if user is None:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Your password is incorrect.")
            else:
                messages.error(request, "An account with this email does not exist. Please sign up.")
            return redirect('counselor:login')

        auth_login(request, user)
        return redirect('counselor:dashboard')

    return render(request, 'auth/login.html')

def logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('counseler:home')



def home(request):
        return render(request, 'home.html')

def dashboard(request):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')
    else:
        return render(request, "dashboard.html")
    
def edit_profile(request):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')

    try:
        user = User.objects.get(email=request.session["email"])
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('counselor:login')

    if request.method == "POST":
        fields = [
            'fname', 'lname', 'email', 'grade', 'location', 'citizenship_status',
            'first_gen', 'ethnicity', 'gender', 'college_goals', 'major_goals',
            'class_rank', 'class_size', 'psat', 'sat', 'act', 'school'
        ]
        updates = {field: request.POST.get(field, '').strip() or None for field in fields}

        resume_file = request.FILES.get('resume')
        if resume_file:
            user.resume = resume_file

        if updates['email'] and updates['email'] != user.email:
            try:
                validate_email(updates['email'])
                if User.objects.exclude(pk=user.pk).filter(email=updates['email']).exists():
                    messages.error(request, "That email is already in use.")
                    return redirect('counselor:edit_profile')
                request.session['email'] = updates['email']
            except ValidationError:
                messages.error(request, "Please enter a valid email.")
                return redirect('counselor:edit_profile')

        for key, value in updates.items():
            setattr(user, key, value)

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('counselor:edit_profile') 

    return render(request, "edit_profile.html", {"user": user})
    
@login_required(login_url='counselor:login')
def edit_schedule(request):
    user = request.user

    if request.method == "POST":
        grade_key = request.POST.get('grade')
        name = request.POST.get('name').strip()
        type = int(request.POST.get('type'))
        org = request.POST.get('org').strip()
        sem1_grade = request.POST.get('grade_1')
        sem2_grade = request.POST.get('grade_2')
        ap_score  = request.POST.get('ap')
        ib_score = request.POST.get('ib')

        if not all([grade_key, name, type, org]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('counselor:edit_schedule')

        field_name = GRADE_SCHEDULE_FIELDS.get(grade_key)
        if not field_name:
            messages.error(request, "Invalid grade selected.")
            return redirect('counselor:edit_schedule')

        schedule = getattr(user, field_name)

        course = get_or_create_course(name=name, type=type, organization=org)

        update_schedule_entry(
            schedule=schedule,
            course=course,
            sem1=sem1_grade,
            sem2=sem2_grade,
            ap=ap_score,
            ib=ib_score,
        )

        messages.success(request, f"{course.name} added to your {grade_key} schedule.")
        return redirect('counselor:edit_schedule')

    context = {
        'freshman_sched':  serialize_schedule(user.freshman_schedule),
        'sophomore_sched': serialize_schedule(user.sophomore_schedule),
        'junior_sched':    serialize_schedule(user.junior_schedule),
        'senior_sched':    serialize_schedule(user.senior_schedule),
    }
    return render(request, "edit_schedule.html", context)

@login_required(login_url='counselor:login')
def edit_extracurriculars(request):
    user = request.user

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == "extracurricular":
            name        = request.POST.get('name')
            description = request.POST.get('description')
            position    = request.POST.get('position')
            ec_type     = int(request.POST.get('type'))
            start_date  = request.POST.get('start_date') or None
            end_date    = request.POST.get('end_date') or None

            ec, created = Extracurricular.objects.get_or_create(
                name=name,
                description=description,
                defaults={
                    'position': position,
                    'type': ec_type,
                    'start_date': start_date,
                    'end_date': end_date,
                }
            )

            TakenEC.objects.get_or_create(user=user, extracurricular=ec)

        elif form_type == "award":
            name         = request.POST.get('award_name')
            description  = request.POST.get('award_description')
            date_received = request.POST.get('date_received') or None

            award, created = Award.objects.get_or_create(
                name=name,
                description=description,
                defaults={'date_received': date_received}
            )

            WonAward.objects.get_or_create(user=user, award=award)

    extracurriculars = serialize_extracurriculars(user.extracurriculars.all())
    awards = user.awards.all()

    return render(request, 'edit_extracurriculars.html', {
        'extracurriculars': extracurriculars,
        'awards': awards,
    })
