from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Core pages
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # User profile
    path('update_profile/', views.update_profile, name='update_profile'),

    # Extracurriculars
    path('extracurriculars/add/', views.add_extracurricular, name='add_extracurricular'),
    path('extracurriculars/edit/<int:pk>/', views.edit_extracurricular, name='edit_extracurricular'),
    path('extracurriculars/delete/<int:pk>/', views.delete_extracurricular, name='delete_extracurricular'),

    # Awards
    path('awards/add/', views.add_award, name='add_award'),
    path('awards/edit/<int:pk>/', views.edit_award, name='edit_award'),
    path('awards/delete/<int:pk>/', views.delete_award, name='delete_award'),

    # College Applications
    path('applications/add/', views.add_college_application, name='add_college_application'),
    path('applications/edit/<int:pk>/', views.edit_college_application, name='edit_college_application'),
    path('applications/delete/<int:pk>/', views.delete_college_application, name='delete_college_application'),

    # Scholarships
    path('scholarships/add/', views.add_scholarship, name='add_scholarship'),
    path('scholarships/edit/<int:pk>/', views.edit_scholarship, name='edit_scholarship'),
    path('scholarships/delete/<int:pk>/', views.delete_scholarship, name='delete_scholarship'),

    # Colleges
    path('colleges/', views.college_list, name='college_list'),
    path('colleges/add/', views.add_college, name='add_college'),

    # Schedules
    path('schedules/<int:grade_level>/', views.manage_schedule, name='manage_schedule'),

    # Chat
    path('chat/<int:user_id>/', views.chat_view, name='chat'),
]
