from contextvars import Context
from operator import contains
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Post, Recycle_Event
import bcrypt
import requests
import urllib
import os
from datetime import date
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

# Create your views here.
