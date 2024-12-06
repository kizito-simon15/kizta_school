from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ParentUser, TeacherUser, BursorUser, SecretaryUser, AcademicUser
from apps.students.models import Student
from apps.staffs.models import Staff  # Import Staff model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class ParentUserCreationForm(CustomUserCreationForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'})
    )
    parent_first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'})
    )
    parent_middle_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'})
    )
    parent_last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'})
    )

    class Meta:
        model = ParentUser
        fields = ['username', 'password1', 'password2', 'student', 'parent_first_name', 'parent_middle_name', 'parent_last_name']
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class StaffUserCreationForm(CustomUserCreationForm):
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.all(),
        widget=forms.Select(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'staff']
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class TeacherUserCreationForm(StaffUserCreationForm):
    class Meta(StaffUserCreationForm.Meta):
        model = TeacherUser
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class BursorUserCreationForm(StaffUserCreationForm):
    class Meta(StaffUserCreationForm.Meta):
        model = BursorUser
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class SecretaryUserCreationForm(StaffUserCreationForm):
    class Meta(StaffUserCreationForm.Meta):
        model = SecretaryUser
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }

class AcademicUserCreationForm(StaffUserCreationForm):
    class Meta(StaffUserCreationForm.Meta):
        model = AcademicUser
        widgets = {
            'username': forms.TextInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password1': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
            'password2': forms.PasswordInput(attrs={'style': 'width: 100%; height: 40px; font-size: 16px;'}),
        }


class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'style': 'padding: 10px; font-size: 18px;',
            }),
        }

