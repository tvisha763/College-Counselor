from django.db import models
from django.forms import CharField
from django.utils import timezone
from django.contrib import admin
from django.conf import settings
import json
from django.contrib.auth.models import AbstractUser

class Course(models.Model):
    name = models.CharField(max_length=1000)
    TYPE = [
        (1, 'Regular'),
        (2, 'Honors'),
        (3, 'AP'),
        (4, 'IB')
    ]
    type = models.IntegerField(default=9, choices=TYPE, blank=True, null=True)
    organization = models.CharField(max_length=1000, blank=True, null=True)
    def __str__(self):
        return '%s - %s' % (self.name, self.type)

class Schedule(models.Model):
    id_phrase = models.CharField(max_length=2000)
    YEAR = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(default=9, choices=YEAR)
    ap_scores = models.JSONField(blank=True, null=True)  # Store as {"Subject1": 5, "Subject2": 4}  
    ib_scores = models.JSONField(blank=True, null=True) 
    grades = models.JSONField(blank=True, null=True)  # Store as {"sem1": {"Subject1": A, "Subject2": B}, "sem2": {"Subject1": A, "Subject2": B}}
    sem1_gpa = models.FloatField(blank=True, null=True)
    sem2_gpa = models.FloatField(blank=True, null=True)
    course = models.ManyToManyField(Course, through='TakenCourse')
    def __str__(self):
        return self.id_phrase
    def calculate_gpa(self, semester_grades):
        grade_to_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        if not semester_grades:
            return None
        total_points = 0
        count = 0
        for grade in semester_grades.values():
            points = grade_to_points.get(grade.upper())
            if points is not None:
                total_points += points
                count += 1
        return round(total_points / count, 2) if count > 0 else None

    def save(self, *args, **kwargs):
        grades = self.grades
        if isinstance(grades, str):
            try:
                grades = json.loads(grades)
            except json.JSONDecodeError:
                grades = {}

        self.sem1_gpa = self.calculate_gpa(grades.get('sem1'))
        self.sem2_gpa = self.calculate_gpa(grades.get('sem2'))
        super().save(*args, **kwargs)

class TakenCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)    
    def __str__(self):
        return '%s - %s' % (self.course, self.schedule)

class TakenCourseInline(admin.TabularInline):
    model = TakenCourse
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = (TakenCourseInline,)

class ScheduleAdmin(admin.ModelAdmin):
    inlines = (TakenCourseInline,)

class Extracurricular(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField()
    position = models.CharField(max_length=1000, blank=True, null=True)

    TYPE = [
        (1, 'Academic'),
        (2, 'Athletics: Club'),
        (3, 'Athletics: JV/Varsity'),
        (4, 'Career Oriented'),
        (5, 'Community Service (Volunteer)'),
        (6, 'Computer/Technology'),
        (7, 'Cultural'),
        (8, 'Dance'),
        (9, 'Debate/Speech'),
        (10, 'Environmental'),
        (11, 'Family Responsibilities'),
        (12, 'Foreign Exchange'),
        (13, 'Foreign Language'),
        (14, 'Internship'),
        (15, 'Journalism/Publication'),
        (16, 'Junior ROTC'),
        (17, 'LGBTQIA+'),
        (18, 'Music: Instrumental'),
        (19, 'Music: Vocal'),
        (20, 'Religious'),
        (21, 'Research'),
        (22, 'Robotics'),
        (23, 'School Spirit'),
        (24, 'Science/Math'),
        (25, 'Social Justice'),
        (26, 'Theater/Drama'),
        (27, 'Work (Paid)'),
        (28, 'Other Club/Activity'),
    ]
    type = models.IntegerField(default=9, choices=TYPE, blank=True, null=True)

    start_date = models.DateField(blank=True, null=True)  
    end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name

class Award(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField()
    date_received = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name

class User(AbstractUser):
    fname = models.CharField(max_length=1000, blank=True, null=True)
    lname = models.CharField(max_length=1000, blank=True, null=True)
    username = None
    email = models.EmailField(max_length=1000, unique=True)
    school = models.CharField(max_length=1000, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    GRADE = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(choices=GRADE, default=9)
    location = models.CharField(max_length=1000)

    CITIZENSHIP = [
        (1, 'Citizen'),
        (2, 'Permanent Resident'),
        (3, 'Visa'),
        (4, 'International')
    ]
    citizenship_status = models.IntegerField(choices=CITIZENSHIP, default=1)

    college_goals = models.TextField(blank=True, null=True)
    major_goals = models.TextField(blank=True, null=True)

    resume = models.FileField(upload_to="resumes/%Y/%m", blank=True, null=True)

    class_rank = models.IntegerField(blank=True, null=True)
    class_size = models.IntegerField(blank=True, null=True)

    FIRST_GEN = [
        (1, 'Not First Gen'),
        (2, 'First Gen')
    ]
    first_gen = models.IntegerField(choices=FIRST_GEN, default=1)

    ethnicity = models.CharField(max_length=1000, blank=True, null=True)
    gender = models.CharField(max_length=1000, blank=True, null=True)

    psat = models.IntegerField(blank=True, null=True)  
    sat = models.IntegerField(blank=True, null=True)
    act = models.IntegerField(blank=True, null=True)

    freshman_schedule = models.OneToOneField('Schedule', on_delete=models.CASCADE, blank=True, null=True, related_name="fresh_sched")
    sophomore_schedule = models.OneToOneField('Schedule', on_delete=models.CASCADE, blank=True, null=True, related_name="soph_sched")
    junior_schedule = models.OneToOneField('Schedule', on_delete=models.CASCADE, blank=True, null=True, related_name="jun_sched")
    senior_schedule = models.OneToOneField('Schedule', on_delete=models.CASCADE, blank=True, null=True, related_name="sen_sched")
    

    extracurriculars = models.ManyToManyField('Extracurricular', through='TakenEC', blank=True)
    awards = models.ManyToManyField('Award', through='WonAward', blank=True)

    def __str__(self):
        return f"{self.fname} {self.lname} - {self.get_grade_display()}"

class TakenEC(models.Model):
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return '%s - %s' % (self.user, self.extracurricular)

class TakenECInline(admin.TabularInline):
    model = TakenEC
    extra = 1

class ECAdmin(admin.ModelAdmin):
    inlines = (TakenECInline,)

class WonAward(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return '%s - %s' % (self.user, self.award)

class WonAwardInline(admin.TabularInline):
    model = WonAward
    extra = 1

class AwardAdmin(admin.ModelAdmin):
    inlines = (WonAwardInline,)

class UserAdmin(admin.ModelAdmin):
    inlines = (TakenECInline, WonAwardInline)


class CollegeApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.CharField(max_length=1000, blank=True, null=True)
    major = models.CharField(default="", max_length=1000, blank=True, null=True)
    alt_major = models.CharField(max_length=1000, blank=True, null=True)

    TYPE = [
        (1, 'Regular Decision'),
        (2, 'Early Decision'),
        (3, 'Early Decision I'),
        (4, 'Early Decision II'),
        (5, 'Early Action'),
        (6, 'Early Action I'),
        (7, 'Early Action II'),
        (8, 'Restrictive Early Action')
    ]
    application_type = models.IntegerField(default=1, choices=TYPE)

    CHANCE = [
        (1, 'Safety'),
        (2, 'Target'),
        (3, 'Reach'),
        (4, 'Far Reach')
    ]
    chance = models.IntegerField(default=1, choices=CHANCE)

    deadline = models.DateField(blank=True, null=True)

    LOCATION = [
        (1, 'In State'),
        (2, 'Out of State'),
        (3, 'International')
    ]
    location = models.IntegerField(default=1, choices=LOCATION)

    STATUS = [
        (1, 'Not Complete'),
        (2, 'Complete')
    ]
    rec_letter_status = models.IntegerField(default=1, choices=STATUS)
    general_questions_status = models.IntegerField(default=1, choices=STATUS)
    grade_report_status = models.IntegerField(default=1, choices=STATUS)
    SAT_ACT_score_status = models.IntegerField(default=1, choices=STATUS)
    scholarship_application_status = models.IntegerField(default=1, choices=STATUS)
    FAFSA_application_status = models.IntegerField(default=1, choices=STATUS)

    APP_STATUS = [
        (1, 'In Progress'),
        (2, 'Submitted'),
        (3, 'Admitted'),
        (4, 'Deferred'),
        (5, 'Waitlisted'),
        (6, 'Denied')
    ]
    application_status = models.IntegerField(default=1, choices=APP_STATUS)
    def __str__(self):
        return '%s - %s - %s' % (self.user, self.college, self.application_status)
    
class EssayDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(CollegeApplication, on_delete=models.CASCADE, blank=True, null=True)
    prompt = models.TextField()
    draft = models.TextField()
    def __str__(self):
        return '%s - %s' % (self.user, self.prompt)

class Scholarship(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=1000)  
    college = models.CharField(max_length=1000, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)  
    deadline = models.DateField()  

    APP_STATUS = [
        (1, 'In Progress'),
        (2, 'Submitted'),
        (3, 'Accepted'),
        (4, 'Denied')
    ]
    application_status = models.IntegerField(default=1, choices=APP_STATUS)

    def __str__(self):
        return '%s - %s' % (self.user, self.name, self.application_status)
