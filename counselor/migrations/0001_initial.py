# Generated by Django 5.1.7 on 2025-03-30 04:35

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, default='')),
                ('date_received', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('application_platform', models.URLField(blank=True, max_length=1000, null=True)),
                ('location', models.CharField(blank=True, default='', max_length=255)),
                ('tuition_cost', models.IntegerField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('average_gpa', models.FloatField(blank=True, null=True)),
                ('average_sat', models.IntegerField(blank=True, null=True)),
                ('average_act', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Extracurricular',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('description', models.TextField(blank=True, default='')),
                ('position', models.CharField(blank=True, max_length=1000, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('fname', models.CharField(blank=True, max_length=1000, null=True)),
                ('lname', models.CharField(blank=True, max_length=1000, null=True)),
                ('email', models.CharField(max_length=1000)),
                ('school', models.CharField(blank=True, max_length=1000, null=True)),
                ('location', models.CharField(blank=True, default='', max_length=255)),
                ('grade', models.IntegerField(blank=True, choices=[(9, 'Freshman'), (10, 'Sophomore'), (11, 'Junior'), (12, 'Senior')], null=True)),
                ('citizenship_status', models.IntegerField(blank=True, choices=[(1, 'Citizen'), (2, 'Permanent Resident'), (3, 'International')], null=True)),
                ('class_rank', models.IntegerField(blank=True, null=True)),
                ('class_size', models.IntegerField(blank=True, null=True)),
                ('psat', models.IntegerField(blank=True, null=True)),
                ('sat', models.IntegerField(blank=True, null=True)),
                ('act', models.IntegerField(blank=True, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('preferred_contact_method', models.CharField(choices=[('Email', 'Email'), ('SMS', 'SMS'), ('App', 'App')], default='Email', max_length=10)),
                ('fafsa_status', models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Submitted', 'Submitted'), ('Approved', 'Approved')], default='Not Started', max_length=50)),
                ('groups', models.ManyToManyField(blank=True, related_name='counselor_users', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='counselor_users_permissions', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CollegeApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deadline', models.DateField(default=datetime.datetime(2025, 4, 29, 4, 35, 0, 590652, tzinfo=datetime.timezone.utc))),
                ('application_type', models.IntegerField(choices=[(1, 'Regular Decision'), (2, 'Early Decision'), (3, 'Early Decision I'), (4, 'Early Decision II'), (5, 'Early Action'), (6, 'Early Action I'), (7, 'Early Action II'), (8, 'Restrictive Early Action')], default=1)),
                ('essay_status', models.IntegerField(choices=[(1, 'Not Complete'), (2, 'Complete')], default=1)),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='counselor.college')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EssayDraft',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('prompt', models.TextField()),
                ('draft', models.TextField()),
                ('word_count', models.PositiveIntegerField(default=0)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('college_application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='essays', to='counselor.collegeapplication')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essay_drafts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Essay Draft',
                'verbose_name_plural': 'Essay Drafts',
                'ordering': ['-last_edited'],
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField(choices=[(9, 'Freshman'), (10, 'Sophomore'), (11, 'Junior'), (12, 'Senior')], default=9)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Scholarship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('amount', models.FloatField(blank=True, null=True)),
                ('deadline', models.DateField(default=datetime.datetime(2025, 4, 29, 4, 35, 0, 591286, tzinfo=datetime.timezone.utc))),
                ('application_status', models.IntegerField(choices=[(1, 'In Progress'), (2, 'Submitted'), (3, 'Accepted'), (4, 'Denied')], default=1)),
                ('college', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='counselor.college')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TakenCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(blank=True, max_length=2, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='counselor.course')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='counselor.schedule')),
            ],
        ),
        migrations.AddField(
            model_name='schedule',
            name='courses',
            field=models.ManyToManyField(through='counselor.TakenCourse', to='counselor.course'),
        ),
        migrations.CreateModel(
            name='TakenEC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extracurricular', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='counselor.extracurricular')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WonAward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('award', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='counselor.award')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['sender', 'receiver'], name='counselor_c_sender__df4e23_idx'), models.Index(fields=['timestamp'], name='counselor_c_timesta_55c5a1_idx'), models.Index(fields=['is_read'], name='counselor_c_is_read_8565d8_idx')],
            },
        ),
    ]
