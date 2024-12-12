from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from .models import Service, DesignGallery, Appointment
from django.utils.timezone import now

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin

# Login View
class CustomLoginView(LoginView):
    template_name = 'salon/login.html'
    redirect_authenticated_user = True  # Langsung redirect jika sudah login

# Public Views
class ServiceListView(ListView):
    """Public view to display the list of services."""
    model = Service
    template_name = 'salon/services.html'


class DesignGalleryListView(ListView):
    """Public view to display the nail art gallery."""
    model = DesignGallery
    template_name = 'salon/gallery.html'


# Login-Required Views
from django.utils.timezone import now

from django.views.generic.edit import CreateView
from .forms import AppointmentForm
from .models import Appointment

from django.utils.timezone import now

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    fields = ['service', 'date_time']
    template_name = 'salon/appointment_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
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









class ProfileView(LoginRequiredMixin, TemplateView):
    """Allow logged-in users to view their profile."""
    template_name = 'salon/profile.html'


class CustomLogoutView(LogoutView):
    """Custom logout view to redirect users to the home page after logout."""
    next_page = 'home'  # Redirect ke halaman utama setelah logout


class RegisterView(CreateView):
    """Allow users to register."""
    template_name = 'salon/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')  # Redirect to login after successful registration


class UserAppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'salon/user_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        # Hanya menampilkan appointment milik user yang sedang login
        return Appointment.objects.filter(user=self.request.user).order_by('-date_time')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'salon/edit_profile.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')  # Redirect ke halaman profil setelah berhasil mengedit

    def get_object(self):
        # Hanya memperbolehkan user yang sedang login untuk mengedit profil mereka sendiri
        return self.request.user


class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Appointment
    fields = ['service', 'date_time']
    template_name = 'salon/edit_appointment.html'
    success_url = reverse_lazy('user_appointments')  # Redirect ke daftar appointment

    def test_func(self):
        # Hanya pengguna yang memiliki appointment yang bisa mengeditnya
        appointment = self.get_object()
        return self.request.user == appointment.user

    def form_valid(self, form):
        # Validasi apakah waktu sudah dipesan
        if Appointment.objects.filter(date_time=form.instance.date_time).exclude(pk=self.object.pk).exists():
            form.add_error('date_time', "This time slot is already booked. Please choose a different time.")
            return self.form_invalid(form)
        return super().form_valid(form)


class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Appointment
    template_name = 'salon/delete_appointment.html'
    success_url = reverse_lazy('user_appointments')  # Redirect ke daftar appointment

    def test_func(self):
        # Hanya pengguna yang memiliki appointment yang bisa menghapusnya
        appointment = self.get_object()
        return self.request.user == appointment.user


from datetime import datetime, timedelta
from django.utils.timezone import localtime, now

def get_available_slots_for_today():
    # Waktu buka dan tutup salon
    opening_time = localtime(now()).replace(hour=10, minute=0, second=0, microsecond=0)
    closing_time = localtime(now()).replace(hour=22, minute=0, second=0, microsecond=0)
    
    # Slot yang sudah dipesan
    booked_slots = Appointment.objects.filter(
        date_time__date=now().date()
    ).values_list('date_time', flat=True)
    
    # Buat daftar semua slot per 30 menit
    slots = []
    current_time = opening_time
    while current_time < closing_time:
        if current_time not in booked_slots and current_time >= localtime(now()):
            slots.append(current_time)
        current_time += timedelta(minutes=30)
    
    return slots
