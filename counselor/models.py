from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from datetime import date

class User(AbstractUser):
    # Personal Information
    fname = models.CharField(max_length=1000, blank=True, null=True)
    lname = models.CharField(max_length=1000, blank=True, null=True)
    email = models.CharField(max_length=1000)
    school = models.CharField(max_length=1000, blank=True, null=True)
    location = models.CharField(max_length=255, default="", blank=True)

    # Academic Information
    GRADE_CHOICES = [
        (9, 'Freshman'),
        (10, 'Sophomore'),
        (11, 'Junior'),
        (12, 'Senior')
    ]
    grade = models.IntegerField(choices=GRADE_CHOICES, blank=True, null=True)
    
    # Demographics
    CITIZENSHIP_STATUS = [
        (1, 'Citizen'),
        (2, 'Permanent Resident'),
        (3, 'International')
    ]
    citizenship_status = models.IntegerField(choices=CITIZENSHIP_STATUS, blank=True, null=True)
    
    # Academic Records
    class_rank = models.IntegerField(blank=True, null=True)
    class_size = models.IntegerField(blank=True, null=True)
    psat = models.IntegerField(blank=True, null=True)
    sat = models.IntegerField(blank=True, null=True)
    act = models.IntegerField(blank=True, null=True)
    
    # WebSocket Branch Fields
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

class Course(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(default="", blank=True)
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
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
        return f"{self.user}'s Schedule" if self.user else f"Schedule {self.id}"

class TakenCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.course} in {self.schedule}"

class Extracurricular(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(default="", blank=True)
    position = models.CharField(max_length=1000, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class TakenEC(models.Model):
    extracurricular = models.ForeignKey(Extracurricular, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} - {self.extracurricular}"

class Award(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(default="", blank=True)
    date_received = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class WonAward(models.Model):
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} - {self.award}"


class EssayDraft(models.Model):
    """Model for storing college essay drafts"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='essay_drafts'
    )
    title = models.CharField(max_length=200)
    prompt = models.TextField()
    draft = models.TextField()
    word_count = models.PositiveIntegerField(default=0)
    last_edited = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # College application this essay is for (optional)
    college_application = models.ForeignKey(
        'CollegeApplication',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='essays'
    )
    
    class Meta:
        ordering = ['-last_edited']
        verbose_name = "Essay Draft"
        verbose_name_plural = "Essay Drafts"
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate word count before saving
        self.word_count = len(self.draft.split())
        super().save(*args, **kwargs)
    
    @property
    def character_count(self):
        return len(self.draft)

class Chat(models.Model):
    sender = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.CASCADE,
        db_index=True # performance 
    )
    receiver = models.ForeignKey(
        User,
        related_name="received_messages",
        on_delete=models.CASCADE,
        db_index=True  # performance
    )
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
        ]
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.message[:20]}..."

    def mark_as_read(self):
        """Helper method to update read status"""
        self.is_read = True
        self.save(update_fields=['is_read'])

    @property
    def formatted_timestamp(self):
        """Human-readable timestamp"""
        return self.timestamp.strftime("%b %d, %Y %I:%M %p")

class College(models.Model):
    name = models.CharField(max_length=1000)
    application_platform = models.URLField(max_length=1000, blank=True, null=True)
    location = models.CharField(max_length=255, default="", blank=True)
    tuition_cost = models.IntegerField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    average_gpa = models.FloatField(blank=True, null=True)
    average_sat = models.IntegerField(blank=True, null=True)
    average_act = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class CollegeApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    deadline = models.DateField(default=timezone.now() + timedelta(days=30))
    
    APPLICATION_TYPES = [
        (1, 'Regular Decision'),
        (2, 'Early Decision'),
        (3, 'Early Decision I'),
        (4, 'Early Decision II'),
        (5, 'Early Action'),
        (6, 'Early Action I'),
        (7, 'Early Action II'),
        (8, 'Restrictive Early Action')
    ]
    application_type = models.IntegerField(choices=APPLICATION_TYPES, default=1)
    
    STATUS_CHOICES = [
        (1, 'Not Complete'),
        (2, 'Complete')
    ]
    essay_status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    
    def __str__(self):
        return f"{self.user} - {self.college}"

class Scholarship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    college = models.ForeignKey(College, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    deadline = models.DateField(default=timezone.now() + timedelta(days=30))
    
    APP_STATUS = [
        (1, 'In Progress'),
        (2, 'Submitted'),
        (3, 'Accepted'),
        (4, 'Denied')
    ]
    application_status = models.IntegerField(choices=APP_STATUS, default=1)
    
    def __str__(self):
        return f"{self.user} - {self.name}"

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
