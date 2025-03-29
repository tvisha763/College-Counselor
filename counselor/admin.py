from django.contrib import admin
from .models import User, AcademicProfile, CollegeAndCareerGoals, Extracurricular, Award, CollegeApplication, Scholarship

admin.site.register(AcademicProfile)
admin.site.register(CollegeAndCareerGoals)
admin.site.register(Extracurricular)
admin.site.register(Award)
admin.site.register(CollegeApplication)
admin.site.register(Scholarship)

