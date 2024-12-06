from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.corecode.models import StudentClass

class Student(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    registration_number = models.CharField(max_length=200, unique=True)
    firstname = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, blank=True, null=True)
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(regex=r"^\+255[0-9]{9}$", message="Entered mobile number isn't in a right format!")
    father_mobile_number = models.CharField(validators=[mobile_num_regex], max_length=13, blank=True, default='+255')
    mother_mobile_number = models.CharField(validators=[mobile_num_regex], max_length=13, blank=True, default='+255')

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")
    parent_student_id = models.IntegerField(null=True, blank=True)  # allows null and blank values
    completed = models.BooleanField(default=False)  # New field to track if the student has completed school

    class Meta:
        ordering = ["firstname", "middle_name", "surname"]

    def __str__(self):
        return f"{self.firstname} {self.middle_name} {self.surname} ({self.registration_number})"

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})

    def clean(self):
        # Normalize the phone numbers
        if self.father_mobile_number and self.father_mobile_number.startswith('0'):
            self.father_mobile_number = '+255' + self.father_mobile_number[1:]
        if self.mother_mobile_number and self.mother_mobile_number.startswith('0'):
            self.mother_mobile_number = '+255' + self.mother_mobile_number[1:]
        super(Student, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Student, self).save(*args, **kwargs)


class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")

