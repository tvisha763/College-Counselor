from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Extracurricular, ECAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(EssayDraft)
admin.site.register(College)
admin.site.register(CollegeApplication)
admin.site.register(Scholarship)
