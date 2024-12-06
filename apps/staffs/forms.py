# apps/staffs/forms.py

from django import forms
from .models import StaffAttendance

class StaffAttendanceForm(forms.ModelForm):
    class Meta:
        model = StaffAttendance
        fields = ['is_present']

    def __init__(self, *args, **kwargs):
        super(StaffAttendanceForm, self).__init__(*args, **kwargs)
        self.fields['is_present'].label = "Mark Attendance"
        self.fields['is_present'].widget = forms.CheckboxInput()
