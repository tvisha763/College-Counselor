from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django import forms
from django.contrib.auth import get_user_model

from .forms import *
from .models import *

User = get_user_model()

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    extracurriculars = Extracurricular.objects.filter(takenec__user=user)
    awards = Award.objects.filter(wonaward__user=user)
    college_apps = CollegeApplication.objects.filter(user=user)
    scholarships = Scholarship.objects.filter(user=user)
    schedules = Schedule.objects.filter(user=user)

    return render(request, 'dashboard.html', {
        'user': user,  
        'extracurriculars': extracurriculars,
        'awards': awards,
        'college_apps': college_apps,
        'scholarships': scholarships,
        'schedules': schedules,
    })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'school', 'location',
            'grade', 'class_rank', 'class_size', 'psat', 'sat', 'act',
            'phone_number', 'preferred_contact_method'
        ]
        widgets = {
            'preferred_contact_method': forms.Select(choices=User._meta.get_field('preferred_contact_method').choices),
        }


@login_required
def add_extracurricular(request):
    if request.method == 'POST':
        form = ExtracurricularForm(request.POST)
        if form.is_valid():
            ec = form.save()
            TakenEC.objects.create(user=request.user, extracurricular=ec)
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
    ec = get_object_or_404(TakenEC, id=pk, user=request.user).extracurricular
    if request.method == 'POST':
        form = ExtracurricularForm(request.POST, instance=ec)
        if form.is_valid():
            form.save()
            messages.success(request, 'Extracurricular updated!')
            return redirect('dashboard')
    else:
        form = ExtracurricularForm(instance=ec)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Edit Extracurricular'
    })

@login_required
@require_POST
def delete_extracurricular(request, pk):
    ec = get_object_or_404(TakenEC, id=pk, user=request.user)
    ec.delete()
    messages.success(request, 'Extracurricular deleted!')
    return redirect('dashboard')

@login_required
def add_award(request):
    if request.method == 'POST':
        form = AwardForm(request.POST)
        if form.is_valid():
            award = form.save()
            WonAward.objects.create(user=request.user, award=award)
            messages.success(request, 'Award added!')
            return redirect('dashboard')
    else:
        form = AwardForm()
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Add Award'
    })

@login_required
def edit_award(request, pk):
    award = get_object_or_404(WonAward, id=pk, user=request.user).award
    if request.method == 'POST':
        form = AwardForm(request.POST, instance=award)
        if form.is_valid():
            form.save()
            messages.success(request, 'Award updated!')
            return redirect('dashboard')
    else:
        form = AwardForm(instance=award)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Edit Award'
    })

@login_required
@require_POST
def delete_award(request, pk):
    award = get_object_or_404(WonAward, id=pk, user=request.user)
    award.delete()
    messages.success(request, 'Award deleted!')
    return redirect('dashboard')

class CollegeApplicationForm(forms.ModelForm):
    class Meta:
        model = CollegeApplication
        fields = ['college', 'application_type', 'deadline', 'status', 'notes']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'application_type': "Application Plan"
        }


@login_required
def edit_college_application(request, pk):
    application = get_object_or_404(CollegeApplication, id=pk, user=request.user)
    if request.method == 'POST':
        form = CollegeApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated!')
            return redirect('dashboard')
    else:
        form = CollegeApplicationForm(instance=application)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Edit College Application'
    })

@login_required
@require_POST
def delete_college_application(request, pk):
    application = get_object_or_404(CollegeApplication, id=pk, user=request.user)
    application.delete()
    messages.success(request, 'Application deleted!')
    return redirect('dashboard')

class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = ['name', 'organization', 'amount', 'deadline', 'status', 'requirements']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
        }
@login_required
def edit_scholarship(request, pk):
    scholarship = get_object_or_404(Scholarship, id=pk, user=request.user)
    if request.method == 'POST':
        form = ScholarshipForm(request.POST, instance=scholarship)
        if form.is_valid():
            form.save()
            messages.success(request, 'Scholarship updated!')
            return redirect('dashboard')
    else:
        form = ScholarshipForm(instance=scholarship)
    
    return render(request, 'form_template.html', {
        'form': form,
        'title': 'Edit Scholarship'
    })

@login_required
@require_POST
def delete_scholarship(request, pk):
    scholarship = get_object_or_404(Scholarship, id=pk, user=request.user)
    scholarship.delete()
    messages.success(request, 'Scholarship deleted!')
    return redirect('dashboard')

@login_required
def college_list(request):
    colleges = College.objects.all()
    return render(request, 'college_list.html', {
        'colleges': colleges
    })

@login_required
def add_college(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        location = request.POST.get('location')
        College.objects.create(name=name, location=location)
        messages.success(request, 'College added!')
        return redirect('college_list')
    
    return render(request, 'add_college.html')

@login_required
def chat_view(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    messages = Chat.objects.filter(
        models.Q(sender=request.user, receiver=receiver) |
        models.Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')
    
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('chat', user_id=user_id)
    else:
        form = ChatMessageForm(initial={'receiver': receiver})
    
    return render(request, 'chat/chat_view.html', {
        'messages': messages,
        'form': form,
        'receiver': receiver
    })

@login_required
def manage_schedule(request, grade_level):
    schedule, created = Schedule.objects.get_or_create(
        user=request.user,
        grade=grade_level
    )
    
    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ScheduleForm(instance=schedule)
    
    return render(request, 'schedule_form.html', {
        'form': form,
        'grade_level': grade_level
    })
