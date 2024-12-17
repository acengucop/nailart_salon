from decimal import Decimal
from datetime import timedelta
from django.shortcuts import render
from django.views.generic import ListView, CreateView, TemplateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.timezone import localtime, now
from .models import Service, DesignGallery, Appointment
from .forms import AppointmentForm


class CustomLoginView(LoginView):
    """View untuk login custom."""
    template_name = 'salon/login.html'
    redirect_authenticated_user = True


class ServiceListView(ListView):
    """Menampilkan daftar layanan salon."""
    model = Service
    template_name = 'salon/services.html'


from django.shortcuts import redirect
from .forms import GalleryCommentForm
from .models import DesignGallery, GalleryComment

class DesignGalleryListView(ListView):
    model = DesignGallery
    template_name = 'salon/gallery.html'
    context_object_name = 'object_list'

    def post(self, request, *args, **kwargs):
        form = GalleryCommentForm(request.POST)
        if form.is_valid():
            gallery_id = request.POST.get('gallery_id')
            gallery = DesignGallery.objects.get(id=gallery_id)
            form.instance.user = request.user
            form.instance.gallery = gallery
            form.save()
        return redirect('gallery')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = GalleryCommentForm()
        return context



class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Membuat appointment baru."""
    model = Appointment
    fields = ['service', 'date_time', 'payment_amount']
    template_name = 'salon/appointment_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        service_price = form.instance.service.price
        min_payment = service_price * Decimal('0.3')

        # Validasi jam operasional: 10:00 - 22:00
        date_time = form.instance.date_time
        opening_time = date_time.replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = date_time.replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            form.add_error('date_time', "The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")
            return self.form_invalid(form)

        # Validasi minimal pembayaran 30%
        if not form.instance.payment_amount or form.instance.payment_amount < min_payment:
            form.add_error('payment_amount', f"Minimum payment is 30% of the service price (${min_payment}).")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booked_appointments'] = Appointment.objects.filter(date_time__gte=now()).order_by('date_time')
        context['min_date'] = now()
        context['available_slots'] = get_available_slots_for_today()
        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    """Menampilkan profil user."""
    template_name = 'salon/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Mengupdate profil user."""
    model = User
    template_name = 'salon/edit_profile.html'
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user


class UserAppointmentListView(LoginRequiredMixin, ListView):
    """Menampilkan daftar appointment user."""
    model = Appointment
    template_name = 'salon/user_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.filter(user=self.request.user).order_by('-date_time')


class AppointmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Mengupdate appointment user."""
    model = Appointment
    fields = ['service', 'date_time']
    template_name = 'salon/edit_appointment.html'
    success_url = reverse_lazy('user_appointments')

    def test_func(self):
        return self.request.user == self.get_object().user

    def form_valid(self, form):
        # Validasi jam operasional
        date_time = form.instance.date_time
        opening_time = date_time.replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = date_time.replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            form.add_error('date_time', "The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")
            return self.form_invalid(form)

        # Validasi slot waktu
        if Appointment.objects.filter(date_time=date_time).exclude(pk=self.object.pk).exists():
            form.add_error('date_time', "This time slot is already booked. Please choose a different time.")
            return self.form_invalid(form)

        return super().form_valid(form)


class AppointmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Menghapus appointment user."""
    model = Appointment
    template_name = 'salon/delete_appointment.html'
    success_url = reverse_lazy('user_appointments')

    def test_func(self):
        return self.request.user == self.get_object().user


def get_available_slots_for_today():
    """
    Mengambil slot yang tersedia untuk hari ini setiap 30 menit,
    dimulai dari jam buka (10:00) sampai jam tutup (22:00).
    """
    current_time = localtime(now())
    opening_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)
    closing_time = current_time.replace(hour=22, minute=0, second=0, microsecond=0)

    booked_slots = Appointment.objects.filter(
        date_time__date=current_time.date()
    ).values_list('date_time', flat=True)

    slots = []
    slot_time = opening_time
    while slot_time < closing_time:
        if slot_time not in booked_slots and slot_time >= current_time:
            slots.append(slot_time)
        slot_time += timedelta(minutes=30)

    return slots


class CustomLogoutView(LogoutView):
    """View untuk logout custom."""
    next_page = 'home'


class RegisterView(CreateView):
    """View untuk registrasi user baru."""
    template_name = 'salon/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Appointment, Service, DesignGallery

# Admin can see and update appointments
from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Appointment

class AdminAppointmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'admin/appointments_list.html'
    context_object_name = 'appointments'

    def test_func(self):
        return self.request.user.is_staff  # Hanya admin yang dapat mengakses

    def post(self, request, *args, **kwargs):
        appointment_id = request.POST.get('appointment_id')
        new_status = request.POST.get('status')

        if appointment_id and new_status in ['Approved', 'Rejected']:
            try:
                appointment = Appointment.objects.get(pk=appointment_id)
                appointment.status = new_status
                appointment.save()
                self.success_message = f"Appointment status changed to {new_status}."
            except Appointment.DoesNotExist:
                self.error_message = "Appointment does not exist."
        
        return redirect('admin_appointments')  # Redirect kembali ke halaman yang sama


# Admin can add a new service
class AdminServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Service
    fields = ['name', 'price', 'duration', 'image']
    template_name = 'admin/add_service.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.is_staff

# Admin can add a new image to gallery
class AdminGalleryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DesignGallery
    fields = ['title', 'description', 'image']
    template_name = 'admin/add_gallery.html'
    success_url = reverse_lazy('gallery')

    def test_func(self):
        return self.request.user.is_staff
