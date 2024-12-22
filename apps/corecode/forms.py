from django import forms
from django.forms import ModelForm, modelformset_factory
from .models import (
    AcademicSession,
    AcademicTerm,
    ExamType,
    Installment,
    SiteConfig,
    StudentClass,
    Subject,
    Signature
)

SiteConfigForm = modelformset_factory(
    SiteConfig,
    fields=("key", "value",),
    extra=0,
)


class AcademicSessionForm(ModelForm):
    prefix = "Academic Session"

    class Meta:
        model = AcademicSession
        fields = ["name", "current"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter session name (e.g. 2023/2024)"
            }),
            "current": forms.CheckboxInput(attrs={
                "class": "form-check-input shadow-sm",
                "style": "width:20px; height:20px; border-radius:4px; margin-top:8px;"
            }),
        }
        help_texts = {
            "name": "A unique name for the academic session.",
            "current": "Mark this session as current if it is the active one."
        }


class AcademicTermForm(ModelForm):
    prefix = "Academic Term"

    class Meta:
        model = AcademicTerm
        fields = ["name", "current"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter term name (e.g. First Term, Second Term)",
                "style": "border-radius:50px;"
            }),
            "current": forms.CheckboxInput(attrs={
                "class": "form-check-input shadow-sm",
                "style": "width:30px; height:30px; border-radius:5px; accent-color:#478ed1;"
            })
        }
        help_texts = {
            "name": "Provide a unique name for the academic term. 😊",
            "current": "Mark this term as current if it is the active one."
        }
        labels = {
            "name": "Term Name",
            "current": "Set as Current"
        }

class ExamTypeForm(ModelForm):
    prefix = "Exam Type"

    class Meta:
        model = ExamType
        fields = ["name", "current"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter exam type name (e.g. Mid-Term, Final)",
                "style": "border-radius:50px;"
            }),
            "current": forms.CheckboxInput(attrs={
                "class": "form-check-input shadow-sm",
                "style": "width:30px; height:30px; border-radius:5px; accent-color:#478ed1;"
            })
        }
        help_texts = {
            "name": "Provide a unique name for the exam type. 😊",
            "current": "Mark this exam type as current if it is the active one."
        }
        labels = {
            "name": "Exam Type Name",
            "current": "Set as Current"
        }

class InstallmentForm(ModelForm):
    prefix = "Installment"

    class Meta:
        model = Installment
        fields = ["name", "current"]


class SubjectForm(ModelForm):
    prefix = "Subject"

    class Meta:
        model = Subject
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter subject name (e.g. Mathematics)",
            })
        }
        help_texts = {
            "name": "Enter a unique subject name."
        }


class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = "__all__"
        widgets = {
            "registration_number": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter registration number"
            }),
            "firstname": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter first name"
            }),
            "surname": forms.TextInput(attrs={
                "class": "form-control shadow-sm",
                "placeholder": "Enter surname"
            }),
            "date_of_birth": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control shadow-sm"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control shadow-sm",
                "rows": 3,
                "placeholder": "Enter address"
            }),
        }


class CurrentSessionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        help_text='Click <a href="/session/create/?next=current-session/">here</a> to add new session',
    )
    current_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        help_text='Click <a href="/term/create/?next=current-session/">here</a> to add new term',
    )
    current_exam = forms.ModelChoiceField(
        queryset=ExamType.objects.all(),
        help_text='Click <a href="/exam/create/?next=current-session/">here</a> to add new exam',
    )
    current_install = forms.ModelChoiceField(
        queryset=Installment.objects.all(),
        help_text='Click <a href="/install/create/?next=current-session/">here</a> to add new installment',
    )


class SignatureForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your name',
                'style': 'font-size: 1.2em; padding: 10px;'
            }),
        }

