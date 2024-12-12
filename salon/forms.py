from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'date_time']

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if not date_time:
            raise forms.ValidationError("Please provide a valid date and time.")
        if Appointment.objects.filter(date_time=date_time).exists():
            raise forms.ValidationError("This time slot is already booked. Please choose a different time.")
        return date_time

