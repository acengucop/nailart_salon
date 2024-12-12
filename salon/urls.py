from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
