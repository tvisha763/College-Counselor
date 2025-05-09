# Generated by Django 5.1.7 on 2025-04-26 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counselor_chat', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_identifier', models.CharField(max_length=100, unique=True)),
                ('prompt_text', models.TextField()),
            ],
            options={
                'verbose_name': 'System Prompt',
                'verbose_name_plural': 'System Prompts',
            },
        ),
    ]
