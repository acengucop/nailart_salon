from django.contrib import admin
from .models import UserProfile, Service, Appointment, DesignGallery, Category

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_staff')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration')
    search_fields = ('name',)
    list_filter = ('price',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    # Menampilkan kolom-kolom penting di admin panel
    list_display = ('user', 'service', 'date_time', 'status')  
    # Menambahkan filter berdasarkan status dan tanggal
    list_filter = ('status', 'date_time')  
    # Menambahkan pencarian berdasarkan username dan nama layanan
    search_fields = ('user__username', 'service__name')  
    # Menambahkan tindakan untuk approve/reject langsung
    actions = ['approve_appointments', 'reject_appointments']  

    # Aksi untuk menyetujui janji
    def approve_appointments(self, request, queryset):
        queryset.update(status='Approved')  
        self.message_user(request, "Selected appointments have been approved.")

    # Aksi untuk menolak janji
    def reject_appointments(self, request, queryset):
        queryset.update(status='Rejected')  
        self.message_user(request, "Selected appointments have been rejected.")

    approve_appointments.short_description = "Approve selected appointments"
    reject_appointments.short_description = "Reject selected appointments"
    

@admin.register(DesignGallery)
class DesignGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

