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

    path('profile/', user_profile, name='user_profile'),
    path('profile/update/', update_user, name='update_user'),
]
