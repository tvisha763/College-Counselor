from django.urls import path
from . import views
app_name = 'counselor'
urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('edit_schedule', views.edit_schedule, name='edit_schedule'),
    path('edit_extracurriculars', views.edit_extracurriculars, name='edit_extracurriculars'),
    path('college_search', views.college_search, name='college_search'),
    path('add_college', views.add_college, name="add_college"),
    path('application/<int:app_id>/', views.track_application, name='track_application'),
    path('analyze-essay/', views.analyze_essay, name='analyze_essay'),
    path('tutoring', views.tutoring, name='tutoring'),
]
