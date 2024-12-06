from django.forms import inlineformset_factory, modelformset_factory
from django import forms
from .models import Invoice, InvoiceItem, Receipt
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from django import forms
from .models import Uniform, StudentUniform, UniformType
from apps.students.models import Student
# apps/finance/forms.py
from django import forms
from apps.students.models import Student
from apps.finance.models import Invoice, Uniform, UniformType


InvoiceItemFormset = inlineformset_factory(
    Invoice, InvoiceItem, fields=["description", "amount"], extra=1, can_delete=True
)


InvoiceReceiptFormSet = inlineformset_factory(
    Invoice,
    Receipt,
    fields=("amount_paid", "date_paid", "comment", "payment_method"),  # Include the payment_method field
    extra=0,
    can_delete=True,
)

Invoices = modelformset_factory(Invoice, exclude=(), extra=4)


class SessionInstallFilterForm(forms.Form):
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

class UniformForm(forms.ModelForm):
    class Meta:
        model = Uniform
        fields = ['student', 'student_class', 'uniform_type', 'quantity']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}),
            'student_class': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}),
            'uniform_type': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}),
            'quantity': forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_students = Student.objects.filter(current_status="active", completed=False)
        self.fields['student'].queryset = active_students
        self.fields['student_class'].queryset = StudentClass.objects.all()
        self.fields['student_class'].disabled = False

UniformFormSet = forms.formset_factory(UniformForm, extra=1)

class StudentUniformForm(forms.ModelForm):
    class Meta:
        model = StudentUniform
        fields = ['student', 'amount']
        widgets = {
            'student': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'style': 'font-size: 1.5rem;', 'value': '0'}),
        }

class UniformTypeForm(forms.ModelForm):
    class Meta:
        model = UniformType
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
        }

"""
class DynamicPaymentForm(forms.Form):
    student_name = forms.CharField(label="Student Name", disabled=True, required=False)
    payment_type = forms.ChoiceField(choices=[('invoice', 'Invoice'), ('uniform', 'Uniform')], required=True, label="Payment Type")
    invoice = forms.ModelChoiceField(queryset=Invoice.objects.none(), required=False, label="Select Invoice")
    uniform_type = forms.ModelChoiceField(queryset=UniformType.objects.all(), required=False, label="Uniform Type")
    quantity = forms.ChoiceField(choices=Uniform.QUANTITY_CHOICES, required=False, label="Quantity")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True, label="Amount")
    phone_number = forms.ChoiceField(label="Select Parent's Mobile Number", required=True)

    def __init__(self, *args, **kwargs):
        parent_user = kwargs.pop('parent_user', None)
        super(DynamicPaymentForm, self).__init__(*args, **kwargs)
        if parent_user:
            student = parent_user.student
            self.fields['student_name'].initial = f"{student.firstname} {student.surname}"
            self.fields['invoice'].queryset = Invoice.objects.filter(student=student)
            self.fields['phone_number'].choices = [
                (student.father_mobile_number, f"Father: {student.father_mobile_number}"),
                (student.mother_mobile_number, f"Mother: {student.mother_mobile_number}")
            ]

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')

        if payment_type == 'invoice' and not cleaned_data.get('invoice'):
            self.add_error('invoice', 'Please select an invoice to pay.')

        if payment_type == 'uniform':
            if not cleaned_data.get('uniform_type'):
                self.add_error('uniform_type', 'Please select a uniform type.')
            if not cleaned_data.get('quantity'):
                self.add_error('quantity', 'Please select the quantity.')
            
            # Calculate the price based on the selected uniform and quantity
            uniform_type = cleaned_data.get('uniform_type')
            quantity = cleaned_data.get('quantity')
            quantity_multiplier = 2 if quantity == "Jozi 2" else 1
            price = uniform_type.price * quantity_multiplier
            cleaned_data['amount'] = price

        return cleaned_data
"""

# apps/finance/forms.py

from django import forms
from accounts.models import ParentUser

class DynamicPaymentForm(forms.Form):
    payment_type = forms.ChoiceField(choices=[('invoice', 'Invoice'), ('uniform', 'Uniform')])
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        parent_user = kwargs.pop('parent_user', None)
        super(DynamicPaymentForm, self).__init__(*args, **kwargs)

        # Safely access the student attribute
        if isinstance(parent_user, ParentUser):
            student = getattr(parent_user, 'student', None)
            if student:
                self.fields['student_name'] = forms.CharField(
                    initial=f"{student.firstname} {student.middle_name} {student.surname}",
                    disabled=True
                )
            else:
                self.fields['student_name'] = forms.CharField(
                    initial="No student associated",
                    disabled=True
                )
        else:
            self.fields['student_name'] = forms.CharField(
                initial="Not a ParentUser",
                disabled=True
            )
