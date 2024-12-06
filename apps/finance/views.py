from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView, View
from .forms import InvoiceItemFormset, InvoiceReceiptFormSet,  SessionInstallFilterForm
from .models import Invoice, InvoiceItem, Receipt, SalaryInvoice
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from apps.staffs.models import Staff
from django.shortcuts import render, get_object_or_404, redirect
from .models import Uniform, StudentUniform
from .forms import UniformForm, StudentUniformForm
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass
from django.http import JsonResponse
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm
from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import datetime
from .models import UniformType
from .forms import UniformTypeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UniformForm, UniformFormSet
from .models import AcademicSession, AcademicTerm, Uniform
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# apps/finance/views.py
from django.shortcuts import render, redirect
from django.conf import settings
#from mpesa import MpesaClient
#from mpesa.models import MpesaPayment
from .models import Payment, Invoice, Receipt, StudentUniform, Uniform
from .forms import DynamicPaymentForm

class SalaryInvoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SalaryInvoice
    template_name = 'finance/salary_list.html'
    context_object_name = 'invoices'
    paginate_by = 10
    permission_required = 'finance.view_salaryinvoice'
    permission_denied_message = 'Access Denied'

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.GET.get('q')
        filter_month = self.request.GET.get('month')

        if search_term:
            queryset = queryset.filter(
                Q(staff__surname__icontains=search_term) |
                Q(staff__firstname__icontains=search_term) |
                Q(month__icontains=search_term) |
                Q(issued_date__icontains=search_term)
            )

        if filter_month:
            try:
                filter_date = datetime.strptime(filter_month, '%Y-%m')
                queryset = queryset.filter(month__year=filter_date.year, month__month=filter_date.month)
            except ValueError:
                pass

        # Apply ordering to the queryset
        queryset = queryset.order_by('-month', '-issued_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = self.get_queryset()

        # Get all distinct months for the dropdown
        distinct_months = SalaryInvoice.objects.dates('month', 'month', order='DESC')
        context['distinct_months'] = distinct_months

        # Group invoices by month and calculate totals
        invoices_by_month = {}
        for invoice in invoices:
            month_key = invoice.month.strftime('%Y-%m')
            if month_key not in invoices_by_month:
                invoices_by_month[month_key] = {
                    'month': invoice.month,
                    'total_net_salary': 0,
                    'total_gross_salary': 0,
                    'total_allowances': 0,
                    'total_deductions': 0,
                    'total_given_salary': 0,
                    'invoices': []
                }
            invoices_by_month[month_key]['total_net_salary'] += invoice.net_salary
            invoices_by_month[month_key]['total_gross_salary'] += invoice.gross_salary
            invoices_by_month[month_key]['total_allowances'] += invoice.allowance
            invoices_by_month[month_key]['total_deductions'] += invoice.deductions
            invoices_by_month[month_key]['total_given_salary'] += invoice.total_given_salary
            invoices_by_month[month_key]['invoices'].append(invoice)

        context['invoices_by_month'] = sorted(invoices_by_month.values(), key=lambda x: x['month'], reverse=True)
        return context

def salary_list(request):
    search_term = request.GET.get('q')
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Filter salary invoices by year and month
    invoices = SalaryInvoice.objects.all()

    if year and month:
        invoices = invoices.filter(month__year=year, month__month=month)

    # Apply search filter
    if search_term:
        invoices = invoices.filter(
            Q(staff__firstname__icontains=search_term) |
            Q(staff__middle_name__icontains=search_term) |
            Q(staff__surname__icontains=search_term) |
            Q(month__icontains=search_term) |
            Q(issued_date__icontains=search_term)
        )

    # Calculate total net salary, gross salary, and deductions for the given month
    total_net_salary = invoices.aggregate(total_net_salary=Sum('net_salary'))['total_net_salary'] or 0
    total_gross_salary = invoices.aggregate(total_gross_salary=Sum('gross_salary'))['total_gross_salary'] or 0
    total_deductions = invoices.aggregate(total_deductions=Sum('deductions'))['total_deductions'] or 0

    context = {
        'invoices': invoices,
        'year': year,
        'month': month,
        'search_term': search_term,
        'total_net_salary': total_net_salary,
        'total_gross_salary': total_gross_salary,
        'total_deductions': total_deductions,
    }

    return render(request, 'finance/salary_list.html', context)

class SalaryInvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = SalaryInvoice
    template_name = 'finance/salary_detail.html'
    context_object_name = 'invoice'
    permission_required = 'finance.view_salaryinvoice'
    permission_denied_message = 'Access Denied'

class SalaryInvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SalaryInvoice
    template_name = 'finance/salary_form.html'
    fields = ['staff', 'month', 'gross_salary', 'allowance', 'deductions', 'issued_date', 'remarks']
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.add_salaryinvoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter staff by current_status='active'
        context['staff_list'] = Staff.objects.filter(current_status='active')
        return context

    def form_valid(self, form):
        # Calculate net salary before saving
        form.instance.net_salary = form.instance.gross_salary + form.instance.allowance
        # Calculate total given salary
        form.instance.total_given_salary = form.instance.net_salary - form.instance.deductions
        return super().form_valid(form)


class SalaryInvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SalaryInvoice
    template_name = 'finance/salary_form.html'
    fields = ['staff', 'month', 'gross_salary', 'allowance', 'deductions', 'issued_date', 'remarks']
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.change_salaryinvoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter staff by current_status='active'
        context['staff_list'] = Staff.objects.filter(current_status='active')
        return context


class SalaryInvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SalaryInvoice
    template_name = 'finance/salary_confirm_delete.html'
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.delete_salaryinvoice'
    permission_denied_message = 'Access Denied'


class InvoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Invoice
    template_name = 'invoice_list.html'
    context_object_name = 'invoices'
    permission_required = 'finance.view_invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = AcademicSession.objects.all()
        context['installments'] = Installment.objects.all()
        context['classes'] = StudentClass.objects.all()
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context

class InvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Invoice
    fields = "__all__"
    success_url = "/finance/list"
    permission_required = 'finance.add_invoice'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter students who are active and have not completed school
        form.fields['student'].queryset = Student.objects.filter(current_status="active", completed=False)
        return form

    def get_context_data(self, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = InvoiceItemFormset(self.request.POST, prefix="invoiceitem_set")
        else:
            context["items"] = InvoiceItemFormset(prefix="invoiceitem_set")
        
        # Fetch only active students who have not completed school
        students = Student.objects.filter(current_status="active", completed=False)
        student_data = {student.id: student.current_class.id for student in students}
        context['student_data'] = student_data

        # Get the current session and installment
        current_session = get_object_or_404(AcademicSession, current=True)
        current_installment = get_object_or_404(Installment, current=True)
        context['current_session'] = current_session.id
        context['current_installment'] = current_installment.id
        
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        if self.object.id is not None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)

class InvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Invoice
    fields = ["student", "session", "installment", "class_for", "balance_from_previous_install"]
    permission_required = 'finance.change_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super(InvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(
                self.request.POST, instance=self.object
            )
            context["items"] = InvoiceItemFormset(
                self.request.POST, instance=self.object
            )
        else:
            context["receipts"] = InvoiceReceiptFormSet(instance=self.object)
            context["items"] = InvoiceItemFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('invoice-list')


class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"
    permission_required = 'finance.view_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class SearchStudents(View):
    def get(self, request):
        term = request.GET.get('term')
        students = Student.objects.filter(name__icontains=term)
        data = [{'id': student.id, 'text': student.name} for student in students]
        return JsonResponse(data, safe=False)


class InvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.delete_invoice'
    permission_denied_message = 'Access Denied'

"""
class ReceiptCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.add_receipt'
    permission_denied_message = "Access Denied"

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
            obj.invoice = invoice
            obj.save()
            return super().form_valid(form)
        except Exception as e:
            # Handle any exceptions here
            return HttpResponseRedirect(reverse_lazy("invoice-list"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
        context["invoice"] = invoice
        return context
"""
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

class ReceiptCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.add_receipt'
    permission_denied_message = "Access Denied"

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
            obj.invoice = invoice
            obj.save()
            messages.success(self.request, "Payment added successfully. You can now generate the receipt.")
            return redirect('add_payment', invoice=invoice.pk)
        except Exception as e:
            messages.error(self.request, f"Error: {str(e)}")
            return redirect('invoice-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
        context["invoice"] = invoice
        context["show_receipt_button"] = True  # Show the receipt button
        return context


class ReceiptUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.change_receipt'
    permission_denied_message = 'Access Denied'


class ReceiptDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Receipt
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.delete_receipt'
    permission_denied_message = 'Access Denied'


@login_required
def bulk_invoice(request):
    return render(request, "finance/bulk_invoice.html")


def save_pdf(request):
    invoices = SalaryInvoice.objects.all()  # Assuming you have a SalaryInvoice model
    template_path = 'salary_pdf_template.html'  # Create a template for PDF generation
    context = {'invoices': invoices}
    # Render the template
    template = get_template(template_path)
    html = template.render(context)
    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_invoices.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def print_pdf(request):
    invoices = SalaryInvoice.objects.all().order_by('-issued_date')
    context = {'invoices': invoices}
    html = render_to_string('finance/salary_list.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="salary_invoices.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def receipt_view(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id)
    invoice = receipt.invoice
    student = invoice.student

    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    current_installment = Installment.objects.filter(current=True).first()

    context = {
        'receipt': receipt,
        'invoice': invoice,
        'student': student,
        'current_session': current_session,
        'current_term': current_term,
        'current_installment': current_installment,
    }
    return render(request, 'receipt_template.html', context)


from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Invoice, Receipt

def generate_receipt(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    latest_receipt = invoice.receipt_set.latest('date_paid')
    context = {
        'invoice': invoice,
        'current_date': timezone.now(),
        'latest_receipt': latest_receipt,
    }
    return render(request, 'finance/receipt.html', context)

@login_required
def uniform_list(request):
    current_session = AcademicSession.objects.filter(current=True).first()
    selected_session_id = request.GET.get('session', current_session.id)
    selected_session = AcademicSession.objects.get(id=selected_session_id)
    selected_class_id = request.GET.get('class', None)  # Get the class filter from the URL

    sessions = AcademicSession.objects.all()
    student_classes = StudentClass.objects.all()  # Retrieve all student classes

    # Apply filtering based on selected class, if any
    uniforms = Uniform.objects.filter(session=selected_session)
    if selected_class_id:
        uniforms = uniforms.filter(student_class_id=selected_class_id)

    uniforms = uniforms.order_by('student', 'student_class')

    uniform_data = {}

    for uniform in uniforms:
        student = uniform.student
        student_class = uniform.student_class.name

        key = f"{student.id}_{student_class}"
        if key not in uniform_data:
            student_uniform = StudentUniform.objects.filter(
                student=student, session=selected_session, student_class=uniform.student_class
            ).first()
            
            total_paid = student_uniform.amount if student_uniform else Decimal('0.00')

            types_bought = []
            total_payable = Decimal('0.00')

            # Process each uniform item
            uniform_items = Uniform.objects.filter(
                student=student, session=selected_session, student_class=uniform.student_class
            )

            for item in uniform_items:
                if item.quantity == "Jozi 1":
                    payable = item.uniform_type.price
                elif item.quantity == "Jozi 2":
                    payable = item.uniform_type.price * 2

                total_payable += payable

                # Add uniform type, quantity, and uniform_id to the types_bought list
                types_bought.append({
                    'uniform_type': item.uniform_type.name,
                    'quantity': item.quantity,
                    'uniform_id': item.pk  # Ensure this is passed to the template
                })

            balance = total_paid - total_payable

            uniform_data[key] = {
                'student': student,
                'student_class': student_class,
                'total_paid': total_paid,
                'total_payable': total_payable,
                'balance': balance,
                'types_bought': types_bought,
                'uniform_id': uniform.pk,
                'student_id': student.pk,
                'student_uniform_id': student_uniform.pk if student_uniform else None,
                'student_class_id': uniform.student_class.pk  # Pass the class ID to ensure correct payment association
            }
        else:
            types_bought = []
            total_payable = Decimal('0.00')

            uniform_items = Uniform.objects.filter(
                student=student, session=selected_session, student_class=uniform.student_class
            )

            for item in uniform_items:
                if item.quantity == "Jozi 1":
                    payable = item.uniform_type.price
                elif item.quantity == "Jozi 2":
                    payable = item.uniform_type.price * 2

                total_payable += payable

                # Add uniform type, quantity, and uniform_id to the types_bought list
                types_bought.append({
                    'uniform_type': item.uniform_type.name,
                    'quantity': item.quantity,
                    'uniform_id': item.pk  # Ensure this is passed to the template
                })

            uniform_data[key]['total_payable'] = total_payable
            uniform_data[key]['balance'] = uniform_data[key]['total_paid'] - total_payable
            uniform_data[key]['types_bought'] = types_bought
            uniform_data[key]['student_class_id'] = uniform.student_class.pk  # Ensure class ID is updated

    return render(request, 'finance/uniform_list.html', {
        'uniform_data': uniform_data,
        'sessions': sessions,
        'selected_session': selected_session,
        'student_classes': student_classes,  # Pass the classes to the template
        'selected_class_id': selected_class_id,  # Pass the selected class ID to the template
    })

@login_required
def uniform_create(request):
    if request.method == 'POST':
        formset = UniformFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # Check if the form has data
                    uniform = form.save(commit=False)
                    uniform.session = AcademicSession.objects.filter(current=True).first()
                    uniform.term = AcademicTerm.objects.filter(current=True).first()
                    uniform.save()
            return redirect('uniform_list')
    else:
        formset = UniformFormSet()

    # Create a dictionary mapping student IDs to their current class IDs
    student_class_map = {
        student.id: student.current_class.id for student in Student.objects.filter(current_status="active", completed=False)
    }

    # Create a dictionary mapping uniform type IDs to their prices
    uniform_type_prices = {
        uniform_type.id: float(uniform_type.price) for uniform_type in UniformType.objects.all()
    }

    context = {
        'formset': formset,
        'is_update': False,  # Add context variable for update or create operation
        'student_class_map': student_class_map,  # Pass the student class map to the template
        'uniform_type_prices': uniform_type_prices,  # Pass the uniform type prices to the template
    }

    return render(request, 'finance/uniform_form.html', context)

@login_required
def uniform_detail(request, student_id):
    current_session = AcademicSession.objects.filter(current=True).first()
    student = get_object_or_404(Student, pk=student_id)
    
    uniforms = Uniform.objects.filter(student=student, session=current_session)
    student_uniform = StudentUniform.objects.filter(student=student, session=current_session).first()
    
    total_paid = student_uniform.amount if student_uniform else 0
    total_used = uniforms.aggregate(total=Sum('price'))['total'] or 0
    balance = total_paid - total_used
    
    uniform_data = []
    for uniform in uniforms:
        uniform_data.append({
            'uniform_type': uniform.get_uniform_type_display(),
            'quantity': uniform.quantity,
            'price': uniform.price
        })
    
    context = {
        'student': student,
        'uniform_data': uniform_data,
        'total_paid': total_paid,
        'total_used': total_used,
        'balance': balance
    }
    
    return render(request, 'finance/uniform_detail.html', context)

def uniform_update(request, pk):
    uniform = get_object_or_404(Uniform, pk=pk)
    
    # Prepare the uniform type prices
    uniform_type_prices = {ut.id: str(ut.price) for ut in UniformType.objects.all()}
    
    if request.method == 'POST':
        form = UniformForm(request.POST, instance=uniform)
        if form.is_valid():
            form.save()
            return redirect('uniform_list')
    else:
        form = UniformForm(instance=uniform)
    
    return render(request, 'finance/uniform_update.html', {
        'form': form,
        'uniform_type_prices': uniform_type_prices  # Pass the uniform type prices to the template
    })

def uniform_delete(request, pk):
    uniform = get_object_or_404(Uniform, pk=pk)
    if request.method == 'POST':
        uniform.delete()
        return redirect('uniform_list')
    return render(request, 'finance/uniform_confirm_delete.html', {'uniform': uniform})

# StudentUniform views
def student_uniform_list(request):
    student_uniforms = StudentUniform.objects.all()
    return render(request, 'finance/student_uniform_list.html', {'student_uniforms': student_uniforms})

@login_required
def student_uniform_create(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    student_class_id = request.GET.get('class')  # Get the class ID from the URL parameters
    student_class = get_object_or_404(StudentClass, pk=student_class_id)  # Retrieve the StudentClass instance

    session = AcademicSession.objects.filter(current=True).first()
    term = AcademicTerm.objects.filter(current=True).first()

    # Attempt to get an existing StudentUniform record for the student, session, term, and class
    student_uniform = StudentUniform.objects.filter(
        student=student,
        session=session,
        term=term,
        student_class=student_class
    ).first()

    if request.method == 'POST':
        form = StudentUniformForm(request.POST)
        if form.is_valid():
            amount_to_add = form.cleaned_data['amount']

            if student_uniform:
                # If the record exists, add the new amount to the existing amount
                student_uniform.amount += amount_to_add
            else:
                # If the record does not exist, create a new one
                student_uniform = StudentUniform(
                    student=student,
                    session=session,
                    term=term,
                    student_class=student_class,
                    amount=amount_to_add
                )
            student_uniform.save()
            return redirect('uniform_list')
    else:
        # If the record exists, initialize the form with the current amount
        initial_data = {'student': student}
        if student_uniform:
            initial_data['amount'] = student_uniform.amount

        form = StudentUniformForm(initial=initial_data)

    return render(request, 'finance/student_uniform_form.html', {
        'form': form,
        'student': student,
        'student_class': student_class  # Pass the student_class to the template
    })

@login_required
def student_uniform_update(request, pk):
    student_uniform = get_object_or_404(StudentUniform, pk=pk)
    if request.method == 'POST':
        form = StudentUniformForm(request.POST, instance=student_uniform)
        if form.is_valid():
            form.save()
            return redirect('uniform_list')
    else:
        form = StudentUniformForm(instance=student_uniform)
    return render(request, 'finance/student_uniform_form.html', {'form': form})

def student_uniform_delete(request, pk):
    student_uniform = get_object_or_404(StudentUniform, pk=pk)
    if request.method == 'POST':
        student_uniform.delete()
        return redirect('student_uniform_list')
    return render(request, 'finance/student_uniform_confirm_delete.html', {'student_uniform': student_uniform})


def student_info_api(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    session = AcademicSession.objects.filter(current=True).first()
    term = AcademicTerm.objects.filter(current=True).first()
    student_info = {
        'session': session.name,
        'term': term.name,
        'student_class': student.current_class.name,
    }
    return JsonResponse(student_info)

class SelectLinkView(TemplateView):
    template_name = 'finance/select_link.html'

class UniformTypeListView(ListView):
    model = UniformType
    template_name = 'finance/uniformtype_list.html'
    context_object_name = 'uniform_types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uniform_types = self.get_queryset()

        # Prepare a list of dictionaries with calculated prices
        uniform_type_data = []
        for uniform_type in uniform_types:
            uniform_type_data.append({
                'name': uniform_type.name,
                'price_one': uniform_type.price,
                'price_two': uniform_type.price * 2,
                'id': uniform_type.id,
            })

        # Pass the calculated data to the context
        context['uniform_type_data'] = uniform_type_data
        return context

class UniformTypeCreateView(CreateView):
    model = UniformType
    form_class = UniformTypeForm
    template_name = 'finance/uniformtype_form.html'
    success_url = reverse_lazy('uniformtype_list')

class UniformTypeUpdateView(UpdateView):
    model = UniformType
    form_class = UniformTypeForm
    template_name = 'finance/uniformtype_form.html'
    success_url = reverse_lazy('uniformtype_list')

class UniformTypeDeleteView(DeleteView):
    model = UniformType
    template_name = 'finance/uniformtype_confirm_delete.html'
    success_url = reverse_lazy('uniformtype_list')

@login_required
def get_uniform_price(request):
    uniform_type_name = request.GET.get('type')
    try:
        uniform_type = UniformType.objects.get(name=uniform_type_name)
        return JsonResponse({'price': uniform_type.price})
    except UniformType.DoesNotExist:
        return JsonResponse({'price': 0}, status=404)

@login_required
def get_student_class(request):
    student_id = request.GET.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        return JsonResponse({'current_class': student.current_class.name})
    except Student.DoesNotExist:
        return JsonResponse({'current_class': ''}, status=404)

"""
def initiate_payment(request):
    if request.method == 'POST':
        form = DynamicPaymentForm(request.POST, parent_user=request.user)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            payment_type = form.cleaned_data['payment_type']
            student = request.user.student

            mpesa = MpesaClient()
            response = mpesa.stk_push(
                phone_number,
                amount,
                account_reference="Test123",
                transaction_desc=f"Payment for {student}",
                callback_url=settings.MPESA_CALLBACK_URL
            )

            if response.get('ResponseCode') == '0':
                payment = Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    phone_number=phone_number,
                    transaction_id=response.get('MerchantRequestID'),
                    status='pending'
                )
                payment.metadata = {
                    'payment_type': payment_type,
                    'student_id': student.id
                }
                payment.save()
                return redirect('payment_success')
            else:
                return redirect('payment_failed')
    else:
        form = DynamicPaymentForm(parent_user=request.user)

    return render(request, 'finance/initiate_payment.html', {'form': form})
"""

from accounts.models import ParentUser

# apps/finance/views.py

from accounts.models import ParentUser

from django.shortcuts import render, redirect
from accounts.models import ParentUser

# apps/finance/views.py

def initiate_payment(request):
    print(f"Current User: {request.user}")  # Debugging line
    
    if request.method == 'POST':
        form = DynamicPaymentForm(request.POST, parent_user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_type = form.cleaned_data['payment_type']
            student = getattr(request.user, 'student', None)

            if student:
                # Set the M-Pesa phone number to the specified number
                phone_number = '07620236662'

                mpesa = MpesaClient()
                response = mpesa.stk_push(
                    phone_number,
                    amount,
                    account_reference="Test123",
                    transaction_desc=f"Payment for {student}",
                    callback_url=settings.MPESA_CALLBACK_URL
                )

                if response.get('ResponseCode') == '0':
                    payment = Payment.objects.create(
                        user=request.user,
                        amount=amount,
                        phone_number=phone_number,
                        transaction_id=response.get('MerchantRequestID'),
                        status='pending'
                    )
                    payment.metadata = {
                        'payment_type': payment_type,
                        'student_id': student.id if student else None
                    }
                    payment.save()
                    return redirect('payment_success')
                else:
                    return redirect('payment_failed')
            else:
                return redirect('parent_dashboard')  # Handle case where student is None
    else:
        form = DynamicPaymentForm(parent_user=request.user)

    return render(request, 'finance/initiate_payment.html', {'form': form})

@csrf_exempt
def mpesa_callback(request):
    data = request.body.decode('utf-8')
    payment = MpesaPayment.process_mpesa_callback(data)
    
    if payment.result_code == 0:
        payment_instance = Payment.objects.get(transaction_id=payment.transaction_id)
        payment_instance.status = 'completed'
        payment_instance.save()

        payment_type = payment_instance.metadata.get('payment_type')
        student_id = payment_instance.metadata.get('student_id')
        student = Student.objects.get(id=student_id)
        
        if payment_type == 'invoice':
            invoice = Invoice.objects.get(student=student)
            Receipt.objects.create(
                invoice=invoice,
                amount_paid=payment_instance.amount,
                payment_method='M_PESA',
            )
        elif payment_type == 'uniform':
            uniform = Uniform.objects.get(student=student)
            StudentUniform.objects.create(
                student=student,
                session=uniform.session,
                term=uniform.term,
                student_class=uniform.student_class,
                amount=payment_instance.amount
            )
    else:
        payment_instance.status = 'failed'
        payment_instance.save()

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
