from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import User, Course, Schedule, TakenCourse, Extracurricular, Award, TakenEC, WonAward, EssayDraft, CollegeApplication, Scholarship
import bcrypt
import requests
import urllib
import os
import json
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import pandas as pd
from django.templatetags.static import static
from openai import OpenAI
import ast
from rapidfuzz import process, fuzz
from django.utils.dateparse import parse_date


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

    user = User.objects.get(email=request.session["email"])
    applications = CollegeApplication.objects.filter(user=user)

    return render(request, "dashboard.html", {
        "applications": applications
    })
    
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
    
@csrf_exempt
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

def get_sched_data(sched):
    sched_data = {
        "grades" : sched.grades,
        "ap scores" : sched.ap_scores,
        "ib scores" : sched.ib_scores,
        "sem1 gpa" : sched.sem1_gpa,
        "sem2 gpa" : sched.sem2_gpa
    }
    return(sched_data)

common_words = ['University', 'College', 'Of', 'At', 'The', 'Institute', 'School', 'System', ","]

def clean_name(name):
    return ' '.join([word for word in name.split() if word not in common_words])

@csrf_exempt
def college_search(request):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')
    
    user = User.objects.get(email=request.session["email"])

    file_path = os.path.join(settings.BASE_DIR, 'counselor', 'static', 'College.csv')
    college_dataset = pd.read_csv(file_path, usecols=["Name", "Private","Apps","Accept","Enroll","F.Undergrad","P.Undergrad","Outstate","Room.Board","Books","Personal","S.F.Ratio","Grad.Rate"])



    class College:
        def __init__(self, name, private, apps, accept, enroll, f_undergrad, p_undergrad, outstate, room_board, books_cost, personal_spending, s_f_ratio, grad_rate):
            self.name = name
            self.private = private
            self.apps = apps
            self.accept = accept
            self.enroll = enroll
            self.f_undergrad = f_undergrad
            self.p_undergrad = p_undergrad
            self.outstate = outstate
            self.room_board = room_board
            self.books_cost = books_cost
            self.personal_spending = personal_spending
            self.s_f_ratio = s_f_ratio
            self.grad_rate = grad_rate
            self.acceptance_rate = (accept / apps * 100) if apps > 0 else 0


    colleges = []

    user_data = {
        'school': user.school,
        'grade': user.GRADE[user.grade-9][1],
        'location': user.location,
        'citizenship' : user.CITIZENSHIP[user.citizenship_status-1][1],
        'college goals' : user.college_goals,
        'major goals' : user.major_goals,
        'class rank' : user.class_rank,
        'class size' : user.class_size,
        'first gen status' : user.FIRST_GEN[user.first_gen-1][1],
        'ethnicity' : user.ethnicity,
        'gender' : user.gender,
        'psat' : user.psat,
        'sat' : user.sat,
        'act' : user.act
    }



    ec_str = ""
    for ec in TakenEC.objects.filter(user=user):
        ec_str += json.dumps(ec.extracurricular) + " "

    award_str = ""
    for award in WonAward.objects.filter(user=user):
        award_str += json.dumps(award.award) + " "

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(model="gpt-4",
        messages=[
                {
                    "role": "system", 
                    "content": "You are to suggest 10 colleges for the user to apply to, given the following information. \n User Profile: " + json.dumps(user_data) + "\n Freshman Schedule: " + json.dumps(get_sched_data(user.freshman_schedule)) + "\n Sophomore Schedule: " + json.dumps(get_sched_data(user.sophomore_schedule)) + "\n Junior Schedule: " + json.dumps(get_sched_data(user.junior_schedule)) + "\n Senior Schedule: " + json.dumps(get_sched_data(user.senior_schedule)) + "\n Extracurriculars: " + ec_str + "\n Awards" + award_str + "Respond with 10 college names in the form of a Python list of strings, and nothing else. Make sure to inclued a good ratio of safety, target, and reach schools."
                }
            ],
        )

    target_names = ast.literal_eval(response.choices[0].message.content)

    print(target_names)
    print(type(target_names))

    cleaned_target_names = [clean_name(name) for name in target_names]

    dataset_names = college_dataset["Name"].tolist()
    cleaned_dataset_names = [clean_name(name) for name in dataset_names]

    final_matches = []

    for target, cleaned_target in zip(target_names, cleaned_target_names):
        try:
            best_match = process.extractOne(
                cleaned_target,
                cleaned_dataset_names,
                scorer=fuzz.token_sort_ratio  
            )
            
            if best_match and best_match[1] >= 60: 
                original_match = dataset_names[cleaned_dataset_names.index(best_match[0])]
                
                if any(keyword.lower() in original_match.lower() for keyword in target.split()):
                    final_matches.append(original_match)
                else:
                    continue
            else:
                continue
        except Exception as e:
            continue

    matched_rows = college_dataset[college_dataset["Name"].isin(final_matches)]

    for _, row in matched_rows.iterrows():
        college = College(
            name=row["Name"],
            private=row["Private"],
            apps=row["Apps"],
            accept=row["Accept"],
            enroll=row["Enroll"],
            f_undergrad=row["F.Undergrad"],
            p_undergrad=row["P.Undergrad"],
            outstate=row["Outstate"],
            room_board=row["Room.Board"],
            books_cost=row["Books"],
            personal_spending=row["Personal"],
            s_f_ratio=row["S.F.Ratio"],
            grad_rate=row["Grad.Rate"]
        )
        colleges.append(college)

    context = {
        "colleges" : colleges,
        "search_results" : [],
    }

    if request.method == "POST":
        search = request.POST.get("search")

        search_cleaned = clean_name(search)

        matches = process.extract(
            search_cleaned,
            cleaned_dataset_names,
            scorer=fuzz.token_sort_ratio,
            limit=10,
        )

        for match_name, score, idx in matches:
            if score >= 20:
                row = college_dataset.iloc[idx]
                college = College(
                    name=row["Name"],
                    private=row["Private"],
                    apps=row["Apps"],
                    accept=row["Accept"],
                    enroll=row["Enroll"],
                    f_undergrad=row["F.Undergrad"],
                    p_undergrad=row["P.Undergrad"],
                    outstate=row["Outstate"],
                    room_board=row["Room.Board"],
                    books_cost=row["Books"],
                    personal_spending=row["Personal"],
                    s_f_ratio=row["S.F.Ratio"],
                    grad_rate=row["Grad.Rate"]
                )
                context["search_results"].append(college)

    
    return render(request, 'college_search.html', context)

def add_college(request):
    if not request.session.get('logged_in') or not request.session.get('email'):
        return redirect('counselor:login')
    if request.method == "GET":
        college_name = request.GET.get("college_name")
        user = User.objects.get(email=request.session["email"])
        app = CollegeApplication(
                user=user, 
                college=college_name,
                rec_letter_status=1,
                general_questions_status=1,
                grade_report_status=1,
                SAT_ACT_score_status=1,
                scholarship_application_status=1,
                FAFSA_application_status=1,
                application_status=1
            )
        app.save()
        return redirect('counselor:college_search')
    
def track_application(request, app_id):
    if not request.session.get('logged_in'):
        return redirect('counselor:login')

    user = User.objects.get(email=request.session["email"])
    application = get_object_or_404(CollegeApplication, id=app_id, user=user)

    if request.method == "POST":
        # Mark as finished
        if "mark_finished" in request.POST:
            application.application_status = 2
            application.save()
            return redirect('counselor:track_application', app_id=app_id)

        # Save or update essay draft
        elif request.POST.get("save_draft_only"):
            prompt = request.POST.get("prompt")
            draft_text = request.POST.get("draft")
            draft_id = request.POST.get("edit_draft_id")  # ✅ Fixed name

            if draft_id:
                draft = get_object_or_404(EssayDraft, id=draft_id, user=user, application=application)
                draft.prompt = prompt
                draft.draft = draft_text
                draft.save()
            elif prompt and draft_text:
                EssayDraft.objects.create(
                    user=user,
                    application=application,
                    prompt=prompt,
                    draft=draft_text
                )
            return redirect('counselor:track_application', app_id=app_id)

        # Update application info
        application.major = request.POST.get("major", "")
        application.alt_major = request.POST.get("alt_major", "")
        application.application_type = int(request.POST.get("application_type", 1))
        application.chance = int(request.POST.get("chance", 1))
        application.deadline = parse_date(request.POST.get("deadline")) if request.POST.get("deadline") else None
        application.location = int(request.POST.get("location", 1))
        application.rec_letter_status = 2 if request.POST.get("rec_letter_status") else 1
        application.general_questions_status = 2 if request.POST.get("general_questions_status") else 1
        application.grade_report_status = 2 if request.POST.get("grade_report_status") else 1
        application.SAT_ACT_score_status = 2 if request.POST.get("SAT_ACT_score_status") else 1
        application.scholarship_application_status = 2 if request.POST.get("scholarship_application_status") else 1
        application.FAFSA_application_status = 2 if request.POST.get("FAFSA_application_status") else 1

        if application.application_status != 2:
            application.application_status = 1

        application.save()
        return redirect('counselor:track_application', app_id=app_id)

    essay_drafts = EssayDraft.objects.filter(application=application)

    return render(request, 'track_application.html', {
        'application': application,
        'essay_drafts': essay_drafts
    })



@csrf_exempt
def analyze_essay(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")

        print("📨 Received text:", text)  # Debug incoming text

        system_prompt = """
            You are an expert college admissions counselor.
            Highlight important parts of the student's college essay and give suggestions for improvement.
            Return a JSON array with the format:
            [
            {"text": "important phrase", "suggestion": "explanation or suggestion"},
            ...
            ]
            Only include relevant suggestions. Do not summarize or add fluff.
        """

        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.4,
            )

            raw_content = response.choices[0].message.content.strip()
            print("🧠 GPT raw content:", raw_content)

            import re, json
            json_match = re.search(r'\[\s*{.*?}\s*\]', raw_content, re.DOTALL)
            feedback = json.loads(json_match.group()) if json_match else []

            print("✅ Final highlights:", feedback)
            return JsonResponse({"highlights": feedback})
        except Exception as e:
            print("❌ Error in analyze_essay:", str(e))
            return JsonResponse({"error": str(e)}, status=500)
