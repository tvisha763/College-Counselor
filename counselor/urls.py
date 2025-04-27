from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('edit_schedule', views.edit_schedule, name='edit_schedule'),
    path('edit_extracurriculars', views.edit_extracurriculars, name='edit_extracurriculars'),
]
