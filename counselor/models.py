from django.db import models
from django.forms import CharField
from django.utils import timezone
from django.contrib import admin


# Create your models here.
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
    description = models.TextField()
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
    grades = models.JSONField(blank=True, null=True)  # Store as {"class1": ["year", "sem 1": "B", "sem 2": "B"], "class2": ["year", "sem 1": "B", "sem 2": "B"]}
    sem1_gpa = models.FloatField(blank=True, null=True)
    sem2_gpa = models.FloatField(blank=True, null=True)
    course = models.ManyToManyField(Course, through='TakenCourse')
    def __str__(self):
        return self.id_phrase

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

class User(models.Model):
    fname = models.CharField(max_length=1000)
    lname = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000)
    password = models.CharField(max_length=1000)
    salt = models.CharField(max_length=1023, null=True)

    school = models.CharField(max_length=1000)
    GRADE = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(default=9, choices=GRADE, blank=True, null=True)
    location = models.CharField(max_length=1000)

    CITIZENSHIP = [
        (1, 'Citizen'),
        (2, 'Permanent Resident'),
        (3, 'International')
    ]
    citizenship_status = models.IntegerField(default = 1, choices=CITIZENSHIP, blank=True, null=True)

    college_goals = models.TextField(blank=True, null=True)
    major_goals = models.TextField(blank=True, null=True)

    resume = models.FileField(upload_to="resumes", blank=True, null=True)

    class_rank = models.IntegerField(blank=True, null=True)
    class_size = models.IntegerField(blank=True, null=True)

    FIRST_GEN = [
        (1, 'Not First Gen'),
        (2, 'First Gen')
    ]
    first_gen = models.IntegerField(default=1, choices=FIRST_GEN, blank=True, null=True)

    ethnicity = models.CharField(max_length=1000, blank=True, null=True)
    gender = models.CharField(max_length=1000, blank=True, null=True)

    psat = models.IntegerField(blank=True, null=True)  
    sat = models.IntegerField(blank=True, null=True)
    act = models.IntegerField(blank=True, null=True)

    freshman_schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, blank=True, null=True, related_name="fresh_sched")
    sophomore_schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, blank=True, null=True, related_name="soph_sched")
    junior_schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, blank=True, null=True, related_name="jun_sched")
    senior_schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, blank=True, null=True, related_name="sen_sched")

    

    extracurriculars = models.ManyToManyField(Extracurricular, through='TakenEC', blank=True)
    awards = models.ManyToManyField(Award, through='WonAward', blank=True)

    def __str__(self):
        return self.fname + ' ' + self.lname

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    SENDER = [
        (1, "User"),
        (2, "General Chat"),
        (3, "Tutor Chat"),
        (4, "Essay Chat")
    ]
    sender = models.IntegerField(default=1, choices=SENDER, blank=True, null=True)
    chat = models.CharField(max_length=1000)
    message = models.TextField()
    def __str__(self):
        return '%s - %s' % (self.sender, self.chat)

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

class EssayDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prompt = models.TextField()
    draft = models.TextField()
    def __str__(self):
        return '%s - %s' % (self.user, self.prompt)

class College(models.Model):
    name = models.CharField(max_length=1000)
    application_platform = models.URLField(max_length=1000)
    location = models.CharField(max_length=1000)
    tuition_cost = models.IntegerField()
    website = models.URLField(blank=True, null=True)  
    average_gpa = models.FloatField()  
    average_sat = models.IntegerField(blank=True, null=True)  
    average_act = models.IntegerField(blank=True, null=True)  
    def __str__(self):
        return (self.name, self.location)

class CollegeApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    major = models.CharField(max_length=1000)
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

    deadline = models.DateField()

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
    essay_status = models.IntegerField(default=1, choices=STATUS)
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
        return '%s - %s' % (self.user, self.application_status)

class Scholarship(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=1000)  
    college = models.ForeignKey(College, on_delete=models.CASCADE) 
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