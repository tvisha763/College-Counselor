from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import * 

class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'grade', 'first_gen_status', 'ethnicity', 'fafsa_status']

class AcademicProfileForm(forms.ModelForm):
    class Meta:
        model = AcademicProfile
        fields = ['gpa', 'class_rank', 'sat_score', 'act_score', 'ap_scores', 'ib_scores']

class CollegeAndCareerGoalsForm(forms.ModelForm):
    class Meta:
        model = CollegeAndCareerGoals
        fields = ['intended_major', 'career_interest', 'dream_schools', 'safety_schools']

class ExtracurricularForm(forms.ModelForm):
    class Meta:
        model = Extracurricular
        fields = ['name', 'position', 'description', 'start_date', 'end_date']

class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = ['name', 'description', 'date_received']

class CollegeApplicationForm(forms.ModelForm):
    class Meta:
        model = CollegeApplication
        fields = ['college', 'application_status', 'decision_type', 'submission_date', 'essay_link']

class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = ['name', 'amount', 'deadline', 'status']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message', 'receiver']

    receiver = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
