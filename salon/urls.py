from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Halaman utama
    path('', views.ServiceListView.as_view(), name='home'),
    path('gallery/', views.DesignGalleryListView.as_view(), name='gallery'),
    path('appointment/new/', views.AppointmentCreateView.as_view(), name='appointment_new'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('appointments/', views.UserAppointmentListView.as_view(), name='user_appointments'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('appointments/<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='edit_appointment'),
    path('appointments/<int:pk>/delete/', views.AppointmentDeleteView.as_view(), name='delete_appointment'),

    # URL Admin Kustom (gunakan prefix 'dashboard')
    path('dashboard/appointments/', views.AdminAppointmentListView.as_view(), name='admin_appointments'),
    path('dashboard/services/add/', views.AdminServiceCreateView.as_view(), name='add_service'),
    path('dashboard/gallery/add/', views.AdminGalleryCreateView.as_view(), name='add_gallery'),
]

# Tambahkan konfigurasi untuk serving media files saat DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
