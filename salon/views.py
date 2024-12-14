from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.timezone import localtime, now
from decimal import Decimal
from datetime import timedelta
from .models import Service, DesignGallery, Appointment
from .forms import AppointmentForm


# Login View
class CustomLoginView(LoginView):
    template_name = 'salon/login.html'
    redirect_authenticated_user = True


# Public Views
class ServiceListView(ListView):
    model = Service
    template_name = 'salon/services.html'


class DesignGalleryListView(ListView):
    model = DesignGallery
    template_name = 'salon/gallery.html'


# Appointment Views
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    fields = ['service', 'date_time', 'payment_amount']
    template_name = 'salon/appointment_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        service_price = form.instance.service.price
        min_payment = service_price * Decimal('0.3')

        # Validate operating hours
        date_time = form.instance.date_time
        opening_time = date_time.replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = date_time.replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            form.add_error('date_time', "The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")
            return self.form_invalid(form)

        # Validate payment amount
        if not form.instance.payment_amount or form.instance.payment_amount < min_payment:
            form.add_error('payment_amount', f"Minimum payment is 30% of the service price (${min_payment}).")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Slot yang sudah dipesan
        context['booked_appointments'] = Appointment.objects.filter(date_time__gte=now()).order_by('date_time')
        # Tanggal minimal untuk pemesanan
        context['min_date'] = now()
        # Slot yang tersedia untuk hari ini
        context['available_slots'] = get_available_slots_for_today()
        return context

# User Profile Views
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'salon/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'salon/edit_profile.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user


# User Appointment Views
class UserAppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'salon/user_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by('-date_time')


class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Appointment
    fields = ['service', 'date_time']
    template_name = 'salon/edit_appointment.html'
    success_url = reverse_lazy('user_appointments')

    def test_func(self):
        return self.request.user == self.get_object().user

    def form_valid(self, form):
        # Validasi waktu pemesanan dalam jam operasional
        date_time = form.instance.date_time
        opening_time = date_time.replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = date_time.replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            form.add_error('date_time', "The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")
            return self.form_invalid(form)

        # Validasi apakah waktu sudah dipesan
        if Appointment.objects.filter(date_time=date_time).exclude(pk=self.object.pk).exists():
            form.add_error('date_time', "This time slot is already booked. Please choose a different time.")
            return self.form_invalid(form)

        return super().form_valid(form)



class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Appointment
    template_name = 'salon/delete_appointment.html'
    success_url = reverse_lazy('user_appointments')

    def test_func(self):
        return self.request.user == self.get_object().user


# Utility Functions
def get_available_slots_for_today():
    # Waktu buka dan tutup salon berdasarkan zona waktu lokal
    current_time = localtime(now())  # Waktu sekarang dalam zona waktu lokal
    opening_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)
    closing_time = current_time.replace(hour=22, minute=0, second=0, microsecond=0)
    
    # Slot yang sudah dipesan
    booked_slots = Appointment.objects.filter(
        date_time__date=current_time.date()
    ).values_list('date_time', flat=True)

    # Buat daftar semua slot per 30 menit
    slots = []
    slot_time = opening_time
    while slot_time < closing_time:
        # Slot hanya ditampilkan jika belum dipesan dan belum melewati waktu saat ini
        if slot_time not in booked_slots and slot_time >= current_time:
            slots.append(slot_time)
        slot_time += timedelta(minutes=30)
    
    return slots


# Authentication Views
class CustomLogoutView(LogoutView):
    next_page = 'home'


class RegisterView(CreateView):
    template_name = 'salon/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
