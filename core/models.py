from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Mentor(AbstractUser):
    is_mentor = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    name = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(unique=True)
    expertise = models.CharField(max_length=255, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='mentors', blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    experience = models.IntegerField(default=0,blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'

    def testimonial_count(self):
        return self.testimonials.count()


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        return timezone.now() < self.expires_at


class Mentee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='testimonials')
    mentee = models.ForeignKey(Mentee, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.mentee.name if self.mentee else 'Anonymous'} for {self.mentor.name}"


class MentorAvailability(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('mentor', 'day_of_week')
        constraints = [
            models.UniqueConstraint(fields=['mentor', 'day_of_week'], name='unique_availability_per_day')
        ]

    def save(self, *args, **kwargs):
        if MentorAvailability.objects.filter(mentor=self.mentor, day_of_week=self.day_of_week).exclude(
                pk=self.pk).exists():
            raise ValidationError(
                f"This mentor already has availability set for {self.day_of_week}. Please choose a different day.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mentor.name} - {self.day_of_week} ({self.start_time} to {self.end_time})"




