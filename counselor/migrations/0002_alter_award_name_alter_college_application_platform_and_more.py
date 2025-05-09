# Generated by Django 5.1.7 on 2025-03-31 00:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counselor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='award',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='college',
            name='application_platform',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='college',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='collegeapplication',
            name='deadline',
            field=models.DateField(default=datetime.datetime(2025, 4, 30, 0, 16, 10, 668373, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='extracurricular',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='extracurricular',
            name='position',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='scholarship',
            name='deadline',
            field=models.DateField(default=datetime.datetime(2025, 4, 30, 0, 16, 10, 669012, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='scholarship',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='fname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='lname',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
