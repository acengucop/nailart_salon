from django import forms
from django.utils.timezone import localtime
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """
    Form untuk membuat appointment baru.
    """
    class Meta:
        model = Appointment
        fields = ['service', 'date_time', 'payment_amount']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')

        if not date_time:
            raise forms.ValidationError("Please provide a valid date and time.")

        # Jam operasional salon: 10:00 - 22:00
        opening_time = localtime(date_time).replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = localtime(date_time).replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            raise forms.ValidationError("The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")

        # Cek apakah slot waktu sudah dipesan
        if Appointment.objects.filter(date_time=date_time).exists():
            raise forms.ValidationError("This time slot is already booked. Please choose a different time.")

        return date_time

    def clean_payment_amount(self):
        payment_amount = self.cleaned_data.get('payment_amount')
        service = self.cleaned_data.get('service')

        if payment_amount and service:
            minimum_payment = service.price * 0.3  # Minimal 30% dari harga layanan
            if payment_amount < minimum_payment:
                raise forms.ValidationError(
                    f"The payment amount must be at least 30% of the service price (${minimum_payment:.2f})."
                )
        return payment_amount


class AppointmentUpdateForm(forms.ModelForm):
    """
    Form untuk mengupdate appointment yang sudah ada.
    """
    class Meta:
        model = Appointment
        fields = ['service', 'date_time']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')

        if not date_time:
            raise forms.ValidationError("Please provide a valid date and time.")

        # Jam operasional salon: 10:00 - 22:00
        opening_time = localtime(date_time).replace(hour=10, minute=0, second=0, microsecond=0)
        closing_time = localtime(date_time).replace(hour=22, minute=0, second=0, microsecond=0)

        if date_time < opening_time or date_time >= closing_time:
            raise forms.ValidationError("The selected time is outside of salon operating hours (10:00 AM - 10:00 PM).")

        return date_time


from django import forms
from .models import GalleryComment

class GalleryCommentForm(forms.ModelForm):
    class Meta:
        model = GalleryComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
