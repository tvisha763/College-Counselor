from django.db import models
from django.forms import CharField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

class User(AbstractUser):  
    """Extends Django's default user model to store additional user information."""  
    grade = models.CharField(max_length=20, blank=True, null=True)  
    first_gen_status = models.BooleanField(default=False)  
    ethnicity = models.CharField(max_length=255, blank=True, null=True)  
    citizenship_status = models.CharField(max_length=50, choices=[("Citizen", "Citizen"), ("Permanent Resident", "Permanent Resident"), ("International", "International")], blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  
    preferred_contact_method = models.CharField(max_length=10, choices=[("Email", "Email"), ("SMS", "SMS"), ("App", "App")], default="Email")  
    fafsa_status = models.CharField(max_length=50, choices=[("Not Started", "Not Started"), ("In Progress", "In Progress"), ("Submitted", "Submitted"), ("Approved", "Approved")], default="Not Started")

    groups = models.ManyToManyField(Group, related_name="counselor_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="counselor_users_permissions", blank=True)

    def __str__(self):
        return self.username

class AcademicProfile(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  
    class_rank = models.IntegerField(blank=True, null=True)  
    coursework_difficulty = models.TextField(blank=True, null=True)  
    psat_score = models.IntegerField(blank=True, null=True)  
    sat_score = models.IntegerField(blank=True, null=True)  
    act_score = models.IntegerField(blank=True, null=True)  
    ap_scores = models.JSONField(blank=True, null=True)  # Store as {"AP Calc": 5, "AP Physics": 4}  
    ib_scores = models.JSONField(blank=True, null=True)  
    dual_enrollment_courses = models.JSONField(blank=True, null=True)  # List of college courses taken in HS  

    def __str__(self):
        return f"{self.user.username} - Academic Profile"

class CollegeAndCareerGoals(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    intended_major = models.CharField(max_length=255, blank=True, null=True)  
    career_interest = models.CharField(max_length=255, blank=True, null=True)  
    dream_schools = models.ManyToManyField("College", related_name="dream_schools", blank=True)  
    safety_schools = models.ManyToManyField("College", related_name="safety_schools", blank=True)  
    preferred_college_type = models.CharField(max_length=50, choices=[("Public", "Public"), ("Private", "Private"), ("Community College", "Community College"), ("Out-of-State", "Out-of-State")], blank=True, null=True)  
    study_abroad_interest = models.BooleanField(default=False)  
    honors_college_interest = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} - College Goals"

class Extracurricular(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=255)  
    position = models.CharField(max_length=255, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)  
    start_date = models.DateField(blank=True, null=True)  
    end_date = models.DateField(blank=True, null=True)  

    def __str__(self):
        return f"{self.user.username} - {self.name}"  

class Award(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  
    date_received = models.DateField(blank=True, null=True)  

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class College(models.Model):  
    name = models.CharField(max_length=255)  
    location = models.CharField(max_length=255, blank=True, null=True)  
    website = models.URLField(blank=True, null=True)  
    average_gpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  
    average_sat = models.IntegerField(blank=True, null=True)  
    average_act = models.IntegerField(blank=True, null=True)  

    def __str__(self):
        return self.name  

class CollegeApplication(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    college = models.ForeignKey(College, on_delete=models.CASCADE)  
    application_status = models.CharField(max_length=50, choices=[("Not Started", "Not Started"), ("In Progress", "In Progress"), ("Submitted", "Submitted"), ("Accepted", "Accepted"), ("Rejected", "Rejected")], default="Not Started")  
    decision_type = models.CharField(max_length=20, choices=[("Regular", "Regular"), ("Early Action", "Early Action"), ("Early Decision", "Early Decision")], blank=True, null=True)  
    submission_date = models.DateField(blank=True, null=True)  
    essay_link = models.URLField(blank=True, null=True)  # Could be a Google Docs link  

    def __str__(self):
        return f"{self.user.username} - {self.college.name} ({self.application_status})"

class Scholarship(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=255)  
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    deadline = models.DateField(blank=True, null=True)  
    status = models.CharField(max_length=50, choices=[("Not Applied", "Not Applied"), ("Pending", "Pending"), ("Awarded", "Awarded"), ("Rejected", "Rejected")], default="Not Applied")  

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.status})"

