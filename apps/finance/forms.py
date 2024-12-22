# apps/finance/forms.py
from django import forms
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from accounts.models import ParentUser
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from apps.students.models import Student
from .models import Invoice, InvoiceItem, Receipt, Uniform, StudentUniform, UniformType

class InvoiceForm(forms.ModelForm):
    item_description = forms.CharField(
        required=False,
        label="Item Description",
        widget=forms.TextInput(attrs={
            'placeholder': 'E.g. Tuition Fee',
            'class': 'form-control'
        })
    )
    item_amount = forms.IntegerField(
        required=False,
        min_value=0,
        label="Item Amount",
        widget=forms.NumberInput(attrs={
            'placeholder': 'E.g. 5000',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Invoice
        fields = ['student', 'session', 'installment', 'class_for', 'balance_from_previous_install', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'installment': forms.Select(attrs={'class': 'form-control'}),
            'class_for': forms.Select(attrs={'class': 'form-control'}),
            'balance_from_previous_install': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'E.g. 1000'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'amount']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Item description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount'
            }),
        }

class InvoiceReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ["amount_paid", "date_paid", "comment", "payment_method"]
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount paid'
            }),
            'date_paid': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'comment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comment'
            }),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

InvoiceItemFormset = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True
)

InvoiceReceiptFormSet = inlineformset_factory(
    Invoice, Receipt, form=InvoiceReceiptForm, extra=0, can_delete=True
)

Invoices = modelformset_factory(Invoice, exclude=(), extra=4)



# apps/finance/views.py

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormset, InvoiceReceiptFormSet

class InvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_update.html"
    permission_required = 'finance.change_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.object

        if self.request.POST:
            context["items"] = InvoiceItemFormset(self.request.POST, instance=invoice)
            context["receipts"] = InvoiceReceiptFormSet(self.request.POST, instance=invoice)
        else:
            context["items"] = InvoiceItemFormset(instance=invoice)
            context["receipts"] = InvoiceReceiptFormSet(instance=invoice)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context["items"]
        receipt_formset = context["receipts"]

        if form.is_valid() and item_formset.is_valid() and receipt_formset.is_valid():
            self.object = form.save()
            item_formset.instance = self.object
            receipt_formset.instance = self.object
            item_formset.save()
            receipt_formset.save()
            return redirect('invoice-detail', pk=self.object.pk)
        else:
            # Print errors to console for debugging
            print("Form Errors:", form.errors)
            print("Non-field form errors:", form.non_field_errors())
            print("Item Formset Errors:", item_formset.errors, item_formset.non_form_errors())
            print("Receipt Formset Errors:", receipt_formset.errors, receipt_formset.non_form_errors())
            return self.render_to_response(context)

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


UniformFormSet = formset_factory(UniformForm, extra=1)


class StudentUniformForm(forms.ModelForm):
    class Meta:
        model = StudentUniform
        fields = ['student', 'amount']
        widgets = {
            'student': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'font-size: 1.5rem;',
                'value': '0'
            }),
        }


class UniformTypeForm(forms.ModelForm):
    class Meta:
        model = UniformType
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Uniform Type Name'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Price'
            }),
        }


class DynamicPaymentForm(forms.Form):
    payment_type = forms.ChoiceField(
        choices=[('invoice', 'Invoice'), ('uniform', 'Uniform')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Payment Amount'})
    )

    def __init__(self, *args, **kwargs):
        parent_user = kwargs.pop('parent_user', None)
        super().__init__(*args, **kwargs)

        if isinstance(parent_user, ParentUser):
            student = getattr(parent_user, 'student', None)
            if student:
                self.fields['student_name'] = forms.CharField(
                    initial=f"{student.firstname} {student.middle_name if student.middle_name else ''} {student.surname}",
                    disabled=True,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            else:
                self.fields['student_name'] = forms.CharField(
                    initial="No student associated",
                    disabled=True,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
        else:
            self.fields['student_name'] = forms.CharField(
                initial="Not a ParentUser",
                disabled=True,
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
