from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

class Staff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]
    GENDER = [("male", "Male"), ("female", "Female")]
    OCCUPATION_CHOICES = [("teacher", "Teacher"), ("administrator", "Administrator"), ("support_staff", "Support Staff")]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    firstname = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    date_of_admission = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_num_regex = RegexValidator(
        regex="^\+255[0-9]{9}$", message="Entered mobile number isn't in the right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )
    occupation = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True)
    guarantor = models.CharField(max_length=200, blank=True)
    contract_duration = models.CharField(max_length=50, blank=True)
    nida_id = models.CharField(max_length=20, blank=True, null=True)
    tin_number = models.CharField(max_length=20, blank=True, null=True)
    contract_start_date = models.DateField(default=timezone.now)
    contract_end_date = models.DateField(blank=True, null=True)
    passport_photo = models.ImageField(blank=True, upload_to="staffs/passports/")
    others = models.TextField(blank=True)

    class Meta:
        permissions = [
            ("view_staff_list", "Can view staff list"),
            ("view_staff_detail", "Can view staff details"),
        ]

    def __str__(self):
        return f"{self.firstname} {self.middle_name} {self.surname} "

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})

    def clean(self):
        # Normalize the phone number format
        if self.mobile_number and self.mobile_number.startswith('0'):
            self.mobile_number = '+255' + self.mobile_number[1:]
        elif not self.mobile_number.startswith('+255'):
            self.mobile_number = '+255' + self.mobile_number

        super().clean()

    def save(self, *args, **kwargs):
        # Initialize the mobile number with +255 if not set
        if not self.mobile_number.startswith('+255'):
            self.mobile_number = '+255' + self.mobile_number[-9:]  # Ensures only 9 digits after +255

        self.clean()
        super().save(*args, **kwargs)

# apps/staffs/models.py

# models.py

from django.db import models
from django.utils import timezone
from accounts.models import CustomUser

class StaffAttendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)  # Track attendance by date
    is_present = models.BooleanField(default=False)
    time_of_arrival = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')  # Ensure each user has only one attendance record per day

    def __str__(self):
        return f"{self.user.username} - {'Present' if self.is_present else 'Absent'} on {self.date.strftime('%Y-%m-%d')} at {self.time_of_arrival.strftime('%H:%M:%S') if self.time_of_arrival else 'No Arrival Time'}"
