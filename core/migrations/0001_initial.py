# Generated by Django 5.1 on 2024-09-02 13:23

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mentee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mentor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_mentor', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('expertise', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin_profile', models.URLField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('experience', models.IntegerField(blank=True, default=0, null=True)),
                ('company', models.CharField(blank=True, max_length=255, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('categories', models.ManyToManyField(blank=True, related_name='mentors', to='core.category')),
            ],
            options={
                'verbose_name': 'Custom User',
                'verbose_name_plural': 'Custom Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MentorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'Sunday'), (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Testimonial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('rating', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mentee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.mentee')),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testimonials', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
