from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    # Personal Information
    fname = models.CharField(max_length=1000, blank=True, null=True)
    lname = models.CharField(max_length=1000, blank=True, null=True)
    school = models.CharField(max_length=1000, blank=True, null=True)
    location = models.CharField(max_length=1000, blank=True, null=True)
    
    # Academic Information
    GRADE_CHOICES = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(choices=GRADE_CHOICES, blank=True, null=True)
    class_rank = models.IntegerField(blank=True, null=True)
    class_size = models.IntegerField(blank=True, null=True)
    
    # Demographics
    CITIZENSHIP_STATUS = [
        (1, 'Citizen'),
        (2, 'Permanent Resident'),
        (3, 'International')
    ]
    citizenship_status = models.IntegerField(choices=CITIZENSHIP_STATUS, blank=True, null=True)
    ethnicity = models.CharField(max_length=1000, blank=True, null=True)
    gender = models.CharField(max_length=1000, blank=True, null=True)
    
    # Standardized Testing
    psat = models.IntegerField(blank=True, null=True)
    sat = models.IntegerField(blank=True, null=True)
    act = models.IntegerField(blank=True, null=True)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=[("Email", "Email"), ("SMS", "SMS"), ("App", "App")],
        default="Email"
    )
    fafsa_status = models.CharField(
        max_length=50,
        choices=[
            ("Not Started", "Not Started"),
            ("In Progress", "In Progress"),
            ("Submitted", "Submitted"),
            ("Approved", "Approved")
        ],
        default="Not Started"
    )

    # Relationships
    groups = models.ManyToManyField(Group, related_name="counselor_users", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="counselor_users_permissions", 
        blank=True
    )

    def __str__(self):
        return f"{self.fname} {self.lname}" if self.fname else self.username

# Academic Models
class Course(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
    id = models.CharField(max_length=2000, primary_key=True)
    YEAR_CHOICES = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(choices=YEAR_CHOICES, default=9)
    courses = models.ManyToManyField(Course, through='TakenCourse')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user}'s {self.get_grade_display()} Schedule" if self.user else self.id

class TakenCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    semester = models.IntegerField(choices=[(1, 'Fall'), (2, 'Spring')], blank=True, null=True)
    
    def __str__(self):
        return f"{self.course} in {self.schedule}"

# Extracurricular Models
class Extracurricular(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    position = models.CharField(max_length=1000, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class TakenEC(models.Model):
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hours_per_week = models.FloatField(blank=True, null=True)
    weeks_per_year = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user} - {self.extracurricular}"

# Award Models
class Award(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(blank=True, null=True)
    date_received = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class WonAward(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} - {self.award}"

# College Application Models
class College(models.Model):
    name = models.CharField(max_length=1000)
    location = models.CharField(max_length=1000)
    website = models.URLField(blank=True, null=True)
    average_gpa = models.FloatField(blank=True, null=True)
    average_sat = models.IntegerField(blank=True, null=True)
    average_act = models.IntegerField(blank=True, null=True)
    tuition_cost = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class CollegeApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    
    # Application Details
    APPLICATION_TYPES = [
        (1, 'Regular Decision'),
        (2, 'Early Decision'),
        (3, 'Early Action'),
        (4, 'Restrictive Early Action')
    ]
    application_type = models.IntegerField(choices=APPLICATION_TYPES, default=1)
    
    APPLICATION_STATUS = [
        (1, 'Not Started'),
        (2, 'In Progress'),
        (3, 'Submitted'),
        (4, 'Admitted'),
        (5, 'Rejected')
    ]
    status = models.IntegerField(choices=APPLICATION_STATUS, default=1)
    
    major = models.CharField(max_length=1000, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    submission_date = models.DateField(blank=True, null=True)
    essay_link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user} - {self.college}"

# Communication Models
class Chat(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

# Admin Configurations
class TakenCourseInline(admin.TabularInline):
    model = TakenCourse
    extra = 1

class ScheduleAdmin(admin.ModelAdmin):
    inlines = [TakenCourseInline]

class TakenECInline(admin.TabularInline):
    model = TakenEC
    extra = 1

class ExtracurricularAdmin(admin.ModelAdmin):
    inlines = [TakenECInline]

class WonAwardInline(admin.TabularInline):
    model = WonAward
    extra = 1

class AwardAdmin(admin.ModelAdmin):
    inlines = [WonAwardInline]
