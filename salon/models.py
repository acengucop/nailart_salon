from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.DurationField(help_text="Duration of service (HH:MM:SS)")
    image = models.ImageField(upload_to='services/', null=True, blank=True)  # Tambahkan field gambar

    def __str__(self):
        return self.name

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from django.core.exceptions import ValidationError
from django.utils.timezone import now

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def clean(self):
        # Validasi jika date_time tidak None
        if self.date_time:
            # Cek apakah waktu reservasi sudah digunakan
            if Appointment.objects.filter(date_time=self.date_time).exclude(pk=self.pk).exists():
                raise ValidationError({'date_time': "This time slot is already booked. Please choose a different time."})
            
            # Cek apakah waktu di masa lalu
            if self.date_time < now():
                raise ValidationError({'date_time': "The date and time cannot be in the past."})
        else:
            raise ValidationError({'date_time': "Please provide a valid date and time."})



class DesignGallery(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='designs/', max_length=255)  # Perbesar max_length

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

from django import forms
from .models import Appointment

from django import forms

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'date_time']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')

        # Validasi apakah date_time sudah dipesan
        if Appointment.objects.filter(date_time=date_time).exists():
            raise forms.ValidationError("This time slot is already booked. Please choose a different time.")
        
        return date_time

