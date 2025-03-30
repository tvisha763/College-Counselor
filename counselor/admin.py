from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_grade_display', 'school', 'location')
    list_filter = ('grade', 'school', 'citizenship_status')
    search_fields = ('username', 'email', 'fname', 'lname')
    filter_horizontal = ('groups', 'user_permissions')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('fname', 'lname', 'email', 'school', 'location')}),
        ('Academic Info', {'fields': ('grade', 'class_rank', 'class_size')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'average_gpa', 'tuition_cost')
    list_filter = ('location',)
    search_fields = ('name', 'location')
    ordering = ('name',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_grade_display')
    list_filter = ('grade',)
    inlines = [TakenCourseInline]
    raw_id_fields = ('user',)

@admin.register(Extracurricular)
class ExtracurricularAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'start_date', 'end_date')
    search_fields = ('name',)
    inlines = [TakenECInline]

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_received')
    search_fields = ('name',)
    inlines = [WonAwardInline]

@admin.register(CollegeApplication)
class CollegeApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'get_application_type_display', 'get_essay_status_display', 'get_deadline',) 
    list_filter = ('application_type', 'essay_status', 'deadline',)
    search_fields = ('user__username', 'user__email', 'college__name', 'college__location',)
    raw_id_fields = ('user', 'college')
    date_hierarchy = 'deadline'
    list_per_page = 25

    def get_deadline(self, obj):
        return obj.deadline.strftime("%b %d, %Y")  # Format: Jan 01, 2023
    get_deadline.short_description = 'Deadline'
    get_deadline.admin_order_field = 'deadline'

    def get_application_type_display(self, obj):
        return dict(CollegeApplication.APPLICATION_TYPES).get(obj.application_type, '')
    get_application_type_display.short_description = 'Application Type'

    def get_essay_status_display(self, obj):
        return dict(CollegeApplication.STATUS_CHOICES).get(obj.essay_status, '')
    get_essay_status_display.short_description = 'Essay Status'


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'college', 'deadline', 'get_application_status_display')
    list_filter = ('application_status',)
    search_fields = ('name', 'user__username')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__username', 'receiver__username')
    readonly_fields = ('timestamp',)

@admin.register(EssayDraft)
class EssayDraftAdmin(admin.ModelAdmin):
    list_display = ('user', 'prompt_preview')
    search_fields = ('user__username', 'prompt')
    raw_id_fields = ('user',)
    
    def prompt_preview(self, obj):
        return f"{obj.prompt[:50]}..." if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt Preview'

admin.site.register(Course)
admin.site.register(TakenCourse)
admin.site.register(TakenEC)
admin.site.register(WonAward)
