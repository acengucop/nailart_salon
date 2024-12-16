from django.contrib import admin
from django.db.models import Sum
from .models import UserProfile, Service, Appointment, DesignGallery, Category


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin untuk model UserProfile."""
    list_display = ('user', 'phone', 'is_staff')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin untuk model Service."""
    list_display = ('name', 'price', 'duration', 'total_bookings', 'total_income')
    search_fields = ('name',)
    list_filter = ('price',)

    def total_bookings(self, obj):
        return Appointment.objects.filter(service=obj).count()
    total_bookings.short_description = "Total Bookings"

    def total_income(self, obj):
        income = Appointment.objects.filter(service=obj, is_paid=True).aggregate(
            Sum('payment_amount')
        )['payment_amount__sum']
        return f"${income:.2f}" if income else "$0.00"
    total_income.short_description = "Total Income"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin untuk model Appointment."""
    list_display = ('user', 'service', 'date_time', 'status', 'payment_amount', 'is_paid', 'total_income')
    list_filter = ('status', 'date_time', 'is_paid')
    search_fields = ('user__username', 'service__name')
    actions = ['approve_appointments', 'reject_appointments', 'appointment_stats']
    list_editable = ('date_time', 'payment_amount', 'is_paid')


    def total_income(self, obj):
        total = Appointment.objects.aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0
        return f"${total:.2f}"
    total_income.short_description = "Total Income"

    def approve_appointments(self, request, queryset):
        queryset.update(status='Approved')
        self.message_user(request, "Selected appointments have been approved.")
    approve_appointments.short_description = "Approve selected appointments"

    def reject_appointments(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, "Selected appointments have been rejected.")
    reject_appointments.short_description = "Reject selected appointments"

    def appointment_stats(self, request, queryset):
        total_pending = Appointment.objects.filter(status='Pending').count()
        total_approved = Appointment.objects.filter(status='Approved').count()
        total_rejected = Appointment.objects.filter(status='Rejected').count()

        self.message_user(request, f"Pending: {total_pending}, Approved: {total_approved}, Rejected: {total_rejected}")
    appointment_stats.short_description = "Show Appointment Stats"


@admin.register(DesignGallery)
class DesignGalleryAdmin(admin.ModelAdmin):
    """Admin untuk model DesignGallery."""
    list_display = ('title', 'description')
    search_fields = ('title',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin untuk model Category."""
    list_display = ('name',)
