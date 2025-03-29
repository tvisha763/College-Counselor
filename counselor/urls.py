from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    home,
    dashboard,
    update_academic_profile,
    update_college_goals,
    add_extracurricular,
    edit_extracurricular,
    delete_extracurricular,
    add_award,
    edit_award,
    delete_award,
    add_college_application,
    edit_college_application,
    delete_college_application,
    add_scholarship,
    edit_scholarship,
    delete_scholarship,
    college_list,
    add_college
)

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', views.home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),


    path('update_academic_profile/', update_academic_profile, name='update_academic_profile'),
    path('update_college_goals/', update_college_goals, name='update_college_goals'),

    path('add_extracurricular/', add_extracurricular, name='add_extracurricular'),
    path('edit_extracurricular/<int:pk>', edit_extracurricular, name='edit_extracurricular'),
    path('delete_extracurricular/<int:pk>', delete_extracurricular, name='delete_extracurricular'),

    path('add_award/', add_award, name='add_award'),
    path('edit_award/<int:pk>/', edit_award, name='edit_award'),
    path('delete_award/<int:pk>/', delete_award, name='delete_award'),

    path('add_college_application/', add_college_application, name='add_college_application'),
    path('edit_college_application/<int:pk>/', edit_college_application, name='edit_college_application'),
    path('delete_college_application/<int:pk>/', delete_college_application, name='delete_college_application'),

    path('add_scholarship/', add_scholarship, name='add_scholarship'),
    path('edit_scholarship/<int:pk>/', edit_scholarship, name='edit_scholarship'),
    path('delete_scholarship/<int:pk>/', delete_scholarship, name='delete_scholarship'),

    path('colleges/', college_list, name='college_list'),
    path('add_college/', add_college, name='add_college'),

    path('chat/<int:user_id>/', views.chat_view, name='chat'),
]
