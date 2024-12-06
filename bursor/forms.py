from django.forms import inlineformset_factory, modelformset_factory
from django import forms
from apps.finance.models import Invoice, InvoiceItem, Receipt
from apps.corecode.models import AcademicSession, Installment, StudentClass

BursorInvoiceItemFormset = inlineformset_factory(
    Invoice, InvoiceItem, fields=["description", "amount"], extra=1, can_delete=True
)


BursorInvoiceReceiptFormSet = inlineformset_factory(
    Invoice,
    Receipt,
    fields=("amount_paid", "date_paid", "comment", "payment_method"),  # Include the payment_method field
    extra=0,
    can_delete=True,
)

Invoices = modelformset_factory(Invoice, exclude=(), extra=4)


class BursorSessionInstallFilterForm(forms.Form):
    session = forms.ChoiceField(choices=[(None, 'All Sessions')], required=False)
    Install = forms.ChoiceField(choices=[(None, 'All Installments')], required=False)
    class_for = forms.ChoiceField(label='Student Class', choices=[(None, 'All Classes')], required=False)
    student_name = forms.CharField(label='Student Name', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].choices = self.get_session_choices()
        self.fields['Install'].choices = self.get_install_choices()
        self.fields['class_for'].choices = self.get_class_for_choices()

    def get_session_choices(self):
        try:
            return [(None, 'All Sessions')] + list(AcademicSession.objects.values_list('id', 'name'))
        except Exception:
            return [(None, 'All Sessions')]

    def get_install_choices(self):
        try:
            return [(None, 'All Installments')] + list(Installment.objects.values_list('id', 'name'))
        except Exception:
            return [(None, 'All Installments')]

    def get_class_for_choices(self):
        try:
            return [(None, 'All Classes')] + list(StudentClass.objects.values_list('id', 'name'))
        except Exception:
            return [(None, 'All Classes')]

from django import forms
from .models import BursorAnswer

class BursorAnswerForm(forms.ModelForm):
    class Meta:
        model = BursorAnswer
        fields = ['answer', 'audio_answer']
        widgets = {
            'answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your answer here...'
            }),
            'audio_answer': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*'  # Accept only audio files
            }),
        }

    audio_answer = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*'
        }),
        label="Upload an audio file (optional)"
    )
