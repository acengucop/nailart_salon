from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from decimal import Decimal
from django import forms

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
    image = models.ImageField(upload_to='services/', null=True, blank=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def clean(self):
        # Validasi waktu appointment tidak di masa lalu
        if self.date_time and self.date_time < now():
            raise ValidationError({'date_time': "The date and time cannot be in the past."})

        # Validasi apakah slot waktu sudah dipesan
        if Appointment.objects.filter(date_time=self.date_time).exclude(pk=self.pk).exists():
            raise ValidationError({'date_time': "This time slot is already booked. Please choose a different time."})

        # Validasi pembayaran minimal 30%
        if self.payment_amount is not None:
            min_payment = self.service.price * Decimal('0.3')
            if self.payment_amount < min_payment:
                raise ValidationError({
                    'payment_amount': f"The payment amount must be at least 30% of the service price (${min_payment:.2f})."
                })

    def save(self, *args, **kwargs):
        # Perbarui status pembayaran secara otomatis
        if self.payment_amount is not None:
            min_payment = self.service.price * Decimal('0.3')
            self.is_paid = self.payment_amount >= min_payment
        else:
            self.is_paid = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.date_time}"

class DesignGallery(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='designs/', max_length=255)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'date_time', 'payment_amount']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')

        if date_time:
            # Validasi apakah slot waktu sudah dipesan
            if Appointment.objects.filter(date_time=date_time).exists():
                raise forms.ValidationError("This time slot is already booked. Please choose a different time.")

            # Validasi apakah waktu di masa lalu
            if date_time < now():
                raise forms.ValidationError("The selected date and time cannot be in the past.")

        return date_time

    def clean_payment_amount(self):
        payment_amount = self.cleaned_data.get('payment_amount')
        service = self.cleaned_data.get('service')

        if payment_amount and service:
            minimum_payment = service.price * Decimal('0.3')
            if payment_amount < minimum_payment:
                raise forms.ValidationError(f"The payment amount must be at least 30% of the service price (${minimum_payment:.2f}).")

        return payment_amount
