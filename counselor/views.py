from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
import bcrypt
import requests
import urllib
import os
import re, json
from datetime import date
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string
import pandas as pd
from django.templatetags.static import static
from openai import OpenAI
import ast
from rapidfuzz import process, fuzz
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as django_logout

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
        django_logout(request)
    return redirect('counselor:home')



def home(request):
        return render(request, 'home.html')

@login_required(login_url='counselor:login')
def dashboard(request):
    user = request.user 
    applications = CollegeApplication.objects.filter(user=user)

    return render(request, "dashboard.html", {
        "applications": applications
    })

@login_required(login_url='counselor:login')
def edit_profile(request):
    try:
        user = request.user
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

@login_required(login_url='counselor:login')
def college_search(request):
    user = request.user 

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

@login_required(login_url='counselor:login')
def add_college(request):
    if request.method == "GET":
        college_name = request.GET.get("college_name")
        user = request.user
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

@login_required(login_url='counselor:login')
def track_application(request, app_id):
    user = request.user 
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


@login_required(login_url='counselor:login')
def analyze_essay(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            text = data.get("text", "").strip()

            print("📨 Received text:", text[:100])  # Only show first 100 chars for safety

            if not text:
                return JsonResponse({"error": "Empty essay text."}, status=400)

            # OpenAI setup
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Prompt emphasizes using exact substrings from essay
            system_prompt = """
                You are an expert college admissions counselor.

                You will be given a student's college essay. Your task is to extract exact sentences or phrases directly from the essay that are either:
                - Strong or meaningful and worth keeping, or
                - In need of improvement with specific, constructive suggestions.

                You MUST return a JSON array of objects in the format:
                [
                {"text": "<exact text from the essay>", "suggestion": "<specific suggestion or reasoning>"},
                ...
                ]

                Rules:
                - DO NOT paraphrase or invent new text. Only copy directly from the essay.
                - DO NOT return explanations outside of the JSON array.
                - Limit each highlighted 'text' to one sentence or phrase (around 5–20 words).
                - Include no more than 10 suggestions.
            """

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.4,
            )

            content = response.choices[0].message.content.strip()
            print("🧠 GPT raw response:", content)

            # Extract just the JSON from GPT response
            json_match = re.search(r'\[\s*{.*?}\s*\]', content, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON array found in response.")

            highlights = json.loads(json_match.group())
            print("✅ Parsed highlights:", highlights)

            return JsonResponse({"highlights": highlights})

        except json.JSONDecodeError as e:
            print("❌ JSON parsing error:", str(e))
            return JsonResponse({"error": "Failed to parse GPT response as JSON."}, status=500)

        except Exception as e:
            print("❌ General error:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST allowed"}, status=405)


@login_required(login_url='counselor:login')
def tutoring(request):
    subject = request.POST.get("subject", "")
    return render(request, 'tutoring.html', {
        'page_identifier': '_tutoring',
        'subject': subject
    })
