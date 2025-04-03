from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    # Personal Information
    first_name = models.CharField(_("first name"), max_length=255, blank=True)
    last_name = models.CharField(_("last name"), max_length=255, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    school = models.CharField(_("school"), max_length=255, blank=True)
    location = models.CharField(_("location"), max_length=255, blank=True)

    # Academic Information
    class Grade(models.IntegerChoices):
        FRESHMAN = 9, _('Freshman')
        SOPHOMORE = 10, _('Sophomore')
        JUNIOR = 11, _('Junior')
        SENIOR = 12, _('Senior')

    grade = models.IntegerField(
        _("grade"),
        choices=Grade.choices,
        blank=True,
        null=True,
        validators=[MinValueValidator(9), MaxValueValidator(12)]
    )
    
    class_rank = models.PositiveIntegerField(
        _("class rank"),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )
    class_size = models.PositiveIntegerField(
        _("class size"),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)]
    )
    psat = models.PositiveIntegerField(
        _("PSAT score"),
        blank=True,
        null=True,
        validators=[MaxValueValidator(1520)]
    )
    sat = models.PositiveIntegerField(
        _("SAT score"),
        blank=True,
        null=True,
        validators=[MaxValueValidator(1600)]
    )
    act = models.PositiveIntegerField(
        _("ACT score"),
        blank=True,
        null=True,
        validators=[MaxValueValidator(36)]
    )

    # Contact Information
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    preferred_contact_method = models.CharField(
        _("preferred contact method"),
        max_length=10,
        choices=[
            ("EMAIL", _("Email")),
            ("SMS", _("SMS")),
            ("APP", _("App"))
        ],
        default="EMAIL"
    )

    # Permissions
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_("The groups this user belongs to."),
        related_name="counselor_users",
        related_query_name="counselor_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="counselor_users_permissions",
        related_query_name="counselor_user_permission",
    )

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def graduation_year(self):
        if self.grade:
            current_year = timezone.now().year
            return current_year + (12 - self.grade)
        return None

class Course(models.Model):
    name = models.CharField(_("name"), max_length=255)
    code = models.CharField(_("course code"), max_length=20, blank=True)
    description = models.TextField(_("description"), blank=True)
    
    class Meta:
        verbose_name = _("course")
        verbose_name_plural = _("courses")
        ordering = ["name"]

    def __str__(self):
        return self.name

class Schedule(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name=_("user")
    )
    year = models.PositiveIntegerField(
        _("academic year"),
        choices=User.Grade.choices
    )
    courses = models.ManyToManyField(
        Course,
        through="EnrolledCourse",
        verbose_name=_("courses")
    )

    class Meta:
        verbose_name = _("schedule")
        verbose_name_plural = _("schedules")
        unique_together = ("user", "year")
        ordering = ["-year"]

    def __str__(self):
        return f"{self.user}'s {self.get_year_display()} Schedule"

class EnrolledCourse(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name="enrolled_courses"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    grade = models.CharField(
        _("grade"),
        max_length=2,
        blank=True,
        validators=[RegexValidator(r'^[A-F][+-]?$')]
    )

    class Meta:
        verbose_name = _("enrolled course")
        verbose_name_plural = _("enrolled courses")
        unique_together = ("schedule", "course")

    def __str__(self):
        return f"{self.course} - {self.grade}"

class Extracurricular(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="", blank=True)
    position = models.CharField(max_length=255, blank=True, null=True)
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
    name = models.CharField(max_length=255)
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
    name = models.CharField(max_length=255)
    application_platform = models.URLField(max_length=255, blank=True, null=True)
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
    name = models.CharField(max_length=255)
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
