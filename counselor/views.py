from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
import requests
import urllib
import os
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import * 
from .models import *

def home(request):
    return render(request, 'dashboard.html')

@login_required
def update_user(request):
    user = request.user
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
        else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/update_user.html', {'form': form})

@login_required
def user_profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

# User dashboard
@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'extracurriculars': user.extracurriculars.all(),
        'awards': user.awards.all(),
        'applications': user.applications.select_related('college'),
        'scholarships': user.scholarships.all(),
        'schedules': user.schedules.prefetch_related('courses')
    }
    return render(request, 'dashboard.html', context)

# Form views for adding/updating user data
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Update Profile'
    })

@login_required
def update_college_goals(request):
    if request.method == 'POST':
        form = CollegeGoalsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CollegeGoalsForm(instance=request.user)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Update College & Career Goals'
    })

@login_required
def add_extracurricular(request):
    if request.method == 'POST':
        form = ExtracurricularForm(request.POST)
        if form.is_valid():
            ec = form.save(commit=False)
            ec.user = request.user
            ec.save()
            messages.success(request, 'Extracurricular added!')
            return redirect('dashboard')
    else:
        form = ExtracurricularForm()
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Add Extracurricular'
    })

@login_required
def edit_extracurricular(request, pk):
    extracurricular = Extracurricular.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        form = ExtracurricularForm(request.POST, instance=extracurricular)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExtracurricularForm(instance=extracurricular)
    return render(request, 'form_template.html', {'form': form, 'title': 'Edit Extracurricular'})

@login_required
def delete_extracurricular(request, pk):
    extracurricular = Extracurricular.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        extracurricular.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': extracurricular})

@login_required
def add_award(request):
    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            award = form.save(commit=False)
            award.user = request.user
            award.save()
            return redirect('dashboard')
    else:
        form = AwardForm()
    return render(request, 'form_template.html', {'form': form, 'title': 'Add Award'})

@login_required
def edit_award(request, pk):
    award = Award.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        form = AwardForm(request.POST, instance=award)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AwardForm(instance=award)
    return render(request, 'form_template.html', {'form': form, 'title': 'Edit Award'})

@login_required
def delete_award(request, pk):
    award = Award.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        award.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': award})

@login_required
def add_college_application(request):
    if request.method == 'POST':
        form = CollegeApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            return redirect('dashboard')
    else:
        form = CollegeApplicationForm()
    return render(request, 'form_template.html', {'form': form, 'title': 'Add College Application'})

@login_required
def edit_college_application(request, pk):
    application = CollegeApplication.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        form = CollegeApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CollegeApplicationForm(instance=application)
    return render(request, 'form_template.html', {'form': form, 'title': 'Edit College Application'})

@login_required
def delete_college_application(request, pk):
    application = CollegeApplication.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        application.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': application})

@login_required
def add_scholarship(request):
    if request.method == 'POST':
        form = ScholarshipForm(request.POST)
        if form.is_valid():
            scholarship = form.save(commit=False)
            scholarship.user = request.user
            scholarship.save()
            return redirect('dashboard')
    else:
        form = ScholarshipForm()
    return render(request, 'form_template.html', {'form': form, 'title': 'Add Scholarship'})

@login_required
def edit_scholarship(request, pk):
    scholarship = Scholarship.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        form = ScholarshipForm(request.POST, instance=scholarship)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ScholarshipForm(instance=scholarship)
    return render(request, 'form_template.html', {'form': form, 'title': 'Edit Scholarship'})

@login_required
def delete_scholarship(request, pk):
    scholarship = Scholarship.objects.get(id=pk, user=request.user)
    if request.method == 'POST':
        scholarship.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'object': scholarship})

@login_required
def college_list(request):
    colleges = College.objects.all()
    return render(request, 'college_list.html', {'colleges': colleges})

@login_required
def add_college(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        website = request.POST.get('website')
        College.objects.create(
            name=name,
            location=location,
            website=website
        )
        return redirect('college_list')
    return render(request, 'add_college.html')

def chat_view(request, user_id):
    receiver = User.objects.get(id=user_id)
    messages = Chat.objects.filter(sender=request.user, receiver=receiver) | Chat.objects.filter(sender=receiver, receiver=request.user)
    messages = messages.order_by('timestamp')
    form = ChatMessageForm(request.POST or None, initial={'receiver': receiver})

    if form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.save()
        return redirect('chat', user_id=user_id)

    return render(request, 'chat/chat_view.html', {'messages': messages, 'form': form, 'receiver': receiver})
