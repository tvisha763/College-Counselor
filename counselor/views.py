from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Course, Schedule, TakenCourse, Extracurricular, Award, TakenEC, WonAward, EssayDraft, College, CollegeApplication, Scholarship
import bcrypt
import requests
import urllib
import os
import json
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# MAKE SURE TO USE THESE?
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

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
                return redirect('counselor:signup')

            for inp in inputs:
                if inp == '':
                    messages.error(request, "Please input all the information.")
                    return redirect('counselor:signup')

            if password != '' and len(password) < 6:
                messages.error(request, "Your password must be at least 6 charecters.")
                return redirect('counselor:signup')

            if "@" not in email:
                messages.error(request, "Please enter your email address.")
                return redirect('counselor:signup')

            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists. If this is you, please log in.")
                return redirect('counselor:signup')

            else:
                salt = bcrypt.gensalt()
                user = User()
                user.email = email
                user.fname = fname
                user.lname = lname
                user.password = bcrypt.hashpw(password, salt)
                fresh_sched = Schedule()
                fresh_sched.id_phrase = email+"_fresh"
                fresh_sched.grade = 9
                fresh_sched.grades = json.dumps({"sem1":{}, "sem2":{}})
                fresh_sched.ap_scores = json.dumps({})
                fresh_sched.ib_scores = json.dumps({})
                fresh_sched.save()
                user.freshman_schedule = fresh_sched
                soph_sched = Schedule()
                soph_sched.id_phrase = email+"_soph"
                soph_sched.grade = 10
                soph_sched.grades = json.dumps({"sem1":{}, "sem2":{}})
                soph_sched.ap_scores = json.dumps({})
                soph_sched.ib_scores = json.dumps({})
                soph_sched.save()
                user.sophomore_schedule = soph_sched
                jun_sched = Schedule()
                jun_sched.id_phrase = email+"_jun"
                jun_sched.grade = 11
                jun_sched.grades = json.dumps({"sem1":{}, "sem2":{}})
                jun_sched.ap_scores = json.dumps({})
                jun_sched.ib_scores = json.dumps({})
                jun_sched.save()
                user.junior_schedule = jun_sched
                sen_sched = Schedule()
                sen_sched.id_phrase = email+"_sen"
                sen_sched.grade = 12
                sen_sched.grades = json.dumps({"sem1":{}, "sem2":{}})
                sen_sched.ap_scores = json.dumps({})
                sen_sched.ib_scores = json.dumps({})
                sen_sched.save()
                user.senior_schedule = sen_sched
                user.salt = salt
                user.save()
                user = User.objects.get(email=email)
                return redirect('counselor:login')
        else:
            if request.session.get('logged_in'):
                return redirect('counselor:login')
    else:
        return redirect('counselor:dashboard')

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
                    return redirect('counselor:login')

            

            if User.objects.filter(email=email).exists():
                saved_hashed_pass = User.objects.filter(email=email).get().password.encode("utf8")[2:-1]
                saved_salt = User.objects.filter(email=email).get().salt.encode("utf8")[2:-1]
                user  = User.objects.filter(email=email).get()
                request.session["email"] = user.email
                request.session['logged_in'] = True
            
                salted_password = bcrypt.hashpw(password, saved_salt)
                if salted_password == saved_hashed_pass:
                    return redirect('counselor:dashboard')
                else:
                    messages.error(request, "Your password is incorrect.")
                    return redirect('counselor:login')

            else:
                messages.error(request, "An account with this email does not exist. Please sign up.")
                return redirect('counselor:login')

        else:
            if request.session.get('logged_in'):
                return redirect('counselor:login')

        return render(request, 'auth/login.html')
    else:
        return redirect('counselor:dashboard')

def logout(request):
    if not request.session.get('logged_in') or not request.session.get('email'):
        return redirect('counselor:login')
    else:
        request.session["email"] = None
        request.session['logged_in'] = False
        return redirect('/')



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
            citizenship = request.POST.get('citizenship_status')
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
    
def edit_schedule(request):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')
    else:
        user = User.objects.get(email=request.session["email"])
        if request.method == "POST":
            grade = request.POST.get('grade')
            #must be unique
            name = request.POST.get('name')
            type  = request.POST.get('type')
            grade_1 = request.POST.get('grade_1')
            grade_2 = request.POST.get('grade_2')
            ap = request.POST.get('ap')
            ib = request.POST.get('ib')
            org = request.POST.get('org')
            print(grade)
            if grade=="freshman":
                if not Course.objects.filter(name=name, organization=org).exists():
                    course = Course()
                    course.name = name
                    course.type  = type
                    course.organization = org
                    course.save()
                else:
                    course = Course.objects.get(name=name, organization=org)
                sched = user.freshman_schedule
                grades_json = json.loads(sched.grades)
                print(grades_json)
                grades_json["sem1"][name] = grade_1
                grades_json["sem2"][name] = grade_2
                sched.grades = json.dumps(grades_json)
                ap_json = json.loads(sched.ap_scores)
                ap_json[name] = ap
                sched.ap_scores = json.dumps(ap_json)
                ib_json = json.loads(sched.ib_scores)
                ib_json[name] = ib
                sched.ib_scores = json.dumps(ib_json)
                sched.save()
                taken_course = TakenCourse()
                taken_course.course = course
                taken_course.schedule = sched
                taken_course.save()
            elif grade=="sophomore":
                if not Course.objects.filter(name=name, organization=org).exists():
                    course = Course()
                    course.name = name
                    course.type  = type
                    course.organization = org
                    course.save()
                else:
                    course = Course.objects.get(name=name, organization=org)
                sched = Schedule.objects.get(id_phrase=user.email+"_soph")
                grades_json = json.loads(sched.grades)
                grades_json["sem1"][name] = grade_1
                grades_json["sem2"][name] = grade_2
                sched.grades = json.dumps(grades_json)
                ap_json = json.loads(sched.ap_scores)
                ap_json[name] = ap
                sched.ap_scores = json.dumps(ap_json)
                ib_json = json.loads(sched.ib_scores)
                ib_json[name] = ib
                sched.ib_scores = json.dumps(ib_json)
                sched.save()
                taken_course = TakenCourse()
                taken_course.course = course
                taken_course.schedule = sched
                taken_course.save()
            elif grade=="junior":
                if not Course.objects.filter(name=name, organization=org).exists():
                    course = Course()
                    course.name = name
                    course.type  = type
                    course.organization = org
                    course.save()
                else:
                    course = Course.objects.get(name=name, organization=org)
                sched = Schedule.objects.get(id_phrase=user.email+"_jun")
                grades_json = json.loads(sched.grades)
                grades_json["sem1"][name] = grade_1
                grades_json["sem2"][name] = grade_2
                sched.grades = json.dumps(grades_json)
                ap_json = json.loads(sched.ap_scores)
                ap_json[name] = ap
                sched.ap_scores = json.dumps(ap_json)
                ib_json = json.loads(sched.ib_scores)
                ib_json[name] = ib
                sched.ib_scores = json.dumps(ib_json)
                sched.save()
                taken_course = TakenCourse()
                taken_course.course = course
                taken_course.schedule = sched
                taken_course.save()
            else:
                if not Course.objects.filter(name=name, organization=org).exists():
                    course = Course()
                    course.name = name
                    course.type  = type
                    course.organization = org
                    course.save()
                else:
                    course = Course.objects.get(name=name, organization=org)
                sched = Schedule.objects.get(id_phrase=user.email+"_sen")
                grades_json = json.loads(sched.grades)
                grades_json["sem1"][name] = grade_1
                grades_json["sem2"][name] = grade_2
                sched.grades = json.dumps(grades_json)
                ap_json = json.loads(sched.ap_scores)
                ap_json[name] = ap
                sched.ap_scores = json.dumps(ap_json)
                ib_json = json.loads(sched.ib_scores)
                ib_json[name] = ib
                sched.ib_scores = json.dumps(ib_json)
                sched.save()
                taken_course = TakenCourse()
                taken_course.course = course
                taken_course.schedule = sched
                taken_course.save()

        class Course_Display():
            def __init__(self, name, type, sem1_grade, sem2_grade, ap, ib, org):
                self.name = name
                if type  == 1:
                    self.type  = "Regular"
                elif type  == 2:
                    self.type  = "Honors"
                elif type  == 3:
                    self.type  = "AP"
                else:
                    self.type  = "IB"
                self.sem1_grade = sem1_grade
                self.sem2_grade = sem2_grade
                self.ap = ap
                self.ib = ib
                self.org = org

        freshman_sched = []
        sophomore_sched = []
        junior_sched = []
        senior_sched =[]

        for taken_course in TakenCourse.objects.filter(schedule = user.freshman_schedule):
            course = taken_course.course
            sched = taken_course.schedule
            name = course.name
            type  = course.type
            sem1_grade = json.loads(sched.grades)["sem1"][name]
            sem2_grade = json.loads(sched.grades)["sem2"][name]
            ap = json.loads(sched.ap_scores)[name]
            ib = json.loads(sched.ib_scores)[name]
            org = course.organization

            freshman_sched.append(Course_Display(name, type, sem1_grade, sem2_grade, ap, ib, org))
        for taken_course in TakenCourse.objects.filter(schedule = user.sophomore_schedule):
            course = taken_course.course
            sched = taken_course.schedule
            name = course.name
            type  = course.type
            sem1_grade = json.loads(sched.grades)["sem1"][name]
            sem2_grade = json.loads(sched.grades)["sem2"][name]
            ap = json.loads(sched.ap_scores)[name]
            ib = json.loads(sched.ib_scores)[name]
            org = course.organization

            sophomore_sched.append(Course_Display(name, type, sem1_grade, sem2_grade, ap, ib, org))
        for taken_course in TakenCourse.objects.filter(schedule = user.junior_schedule):
            course = taken_course.course
            sched = taken_course.schedule
            name = course.name
            type  = course.type
            sem1_grade = json.loads(sched.grades)["sem1"][name]
            sem2_grade = json.loads(sched.grades)["sem2"][name]
            ap = json.loads(sched.ap_scores)[name]
            ib = json.loads(sched.ib_scores)[name]
            org = course.organization

            junior_sched.append(Course_Display(name, type, sem1_grade, sem2_grade, ap, ib, org))
        for taken_course in TakenCourse.objects.filter(schedule = user.senior_schedule):
            course = taken_course.course
            sched = taken_course.schedule
            name = course.name
            type  = course.type
            sem1_grade = json.loads(sched.grades)["sem1"][name]
            sem2_grade = json.loads(sched.grades)["sem2"][name]
            ap = json.loads(sched.ap_scores)[name]
            ib = json.loads(sched.ib_scores)[name]
            org = course.organization

            senior_sched.append(Course_Display(name, type, sem1_grade, sem2_grade, ap, ib, org))
                
        context = {
            "freshman_sched" : freshman_sched,
            "sophomore_sched" : sophomore_sched,
            "junior_sched" : junior_sched,
            "senior_sched" : senior_sched
        }
        return render(request, "edit_schedule.html", context)

def edit_extracurriculars(request):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')

    user = User.objects.get(email=request.session["email"])

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == "extracurricular":
            name = request.POST.get('name')
            description = request.POST.get('description')
            position = request.POST.get('position')
            type = request.POST.get('type')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            ec, created = Extracurricular.objects.get_or_create(
                name=name,
                description=description,
                defaults={
                    'position': position,
                    'type': type,
                    'start_date': start_date or None,
                    'end_date': end_date or None,
                }
            )

            if not TakenEC.objects.filter(user=user, extracurricular=ec).exists():
                TakenEC.objects.create(user=user, extracurricular=ec)

        elif form_type == "award":
            name = request.POST.get('award_name')
            description = request.POST.get('award_description')
            date_received = request.POST.get('date_received')

            award, created = Award.objects.get_or_create(
                name=name,
                description=description,
                defaults={'date_received': date_received or None}
            )

            if not WonAward.objects.filter(user=user, award=award).exists():
                WonAward.objects.create(user=user, award=award)

    class Extracurricular_Display:
        def __init__(self, name, description, position, type, start_date, end_date):
            self.name = name
            self.description = description
            self.position = position
            self.type = Extracurricular.TYPE[type-1][1]
            self.start_date = start_date
            self.end_date = end_date

    extracurriculars = user.extracurriculars.all()
    awards = user.awards.all()
    ec_display = []
    for ec in extracurriculars:
        ec_display.append(Extracurricular_Display(ec.name, ec.description, ec.position, ec.type, ec.start_date, ec.end_date))

    return render(request, 'edit_extracurriculars.html', {
        'extracurriculars': ec_display,
        'awards': awards,
    })
