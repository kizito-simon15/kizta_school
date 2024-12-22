# apps/finance/views.py

from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Sum
from django.forms import inlineformset_factory
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import get_template, render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView, View, TemplateView
from django.views.decorators.csrf import csrf_exempt

from xhtml2pdf import pisa

from accounts.models import ParentUser
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from apps.students.models import Student
from apps.staffs.models import Staff
from expenditures.models import Expenditure

from .forms import (
    InvoiceForm,
    InvoiceItemFormset,
    InvoiceReceiptFormSet,
    SessionInstallFilterForm,
    UniformForm,
    UniformFormSet,
    StudentUniformForm,
    UniformTypeForm,
    DynamicPaymentForm
)
from .models import (
    Invoice, InvoiceItem, Receipt, SalaryInvoice,
    Uniform, StudentUniform, UniformType, Payment
)


# ---------------------------
# SalaryInvoice Views
# ---------------------------
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

        return queryset.order_by('-month', '-issued_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoices = self.object_list
        distinct_months = SalaryInvoice.objects.dates('month', 'month', order='DESC')
        context['distinct_months'] = distinct_months

        # Group invoices by month
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
    invoices = SalaryInvoice.objects.all()

    if year and month:
        invoices = invoices.filter(month__year=year, month__month=month)

    if search_term:
        invoices = invoices.filter(
            Q(staff__firstname__icontains=search_term) |
            Q(staff__middle_name__icontains=search_term) |
            Q(staff__surname__icontains=search_term) |
            Q(month__icontains=search_term) |
            Q(issued_date__icontains=search_term)
        )

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
        context['staff_list'] = Staff.objects.filter(current_status='active')
        return context

    def form_valid(self, form):
        form.instance.net_salary = form.instance.gross_salary + form.instance.allowance
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
        context['staff_list'] = Staff.objects.filter(current_status='active')
        return context


class SalaryInvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SalaryInvoice
    template_name = 'finance/salary_confirm_delete.html'
    success_url = reverse_lazy('salary-invoice-list')
    permission_required = 'finance.delete_salaryinvoice'
    permission_denied_message = 'Access Denied'


# ---------------------------
# Invoice Views
# ---------------------------
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




class InvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "finance/invoice_form.html"
    permission_required = 'finance.add_invoice'
    success_url = reverse_lazy("invoice-list")

    def form_valid(self, form):
        response = super().form_valid(form)
        invoice = self.object
        description = form.cleaned_data.get('item_description')
        amount = form.cleaned_data.get('item_amount')
        if description and amount is not None:
            InvoiceItem.objects.create(invoice=invoice, description=description, amount=amount)
        return response



class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Invoice
    permission_required = 'finance.view_invoice'
    permission_denied_message = 'Access Denied'
    template_name = 'finance/invoice_detail.html'  # Read-only detail template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.object
        # Instead of formsets, we use plain querysets here
        context["items"] = InvoiceItem.objects.filter(invoice=invoice)
        context["receipts"] = Receipt.objects.filter(invoice=invoice)
        return context



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



class InvoiceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Invoice
    success_url = reverse_lazy("invoice-list")
    permission_required = 'finance.delete_invoice'
    permission_denied_message = 'Access Denied'


# ---------------------------
# Student & Class AJAX
# ---------------------------
def student_search(request):
    term = request.GET.get('q', '')
    students = Student.objects.filter(
        firstname__icontains=term,
        current_status="active",
        completed=False
    )[:50]

    results = [{"id": s.id, "text": f"{s.firstname} {s.surname}"} for s in students]
    return JsonResponse({"results": results})


def get_student_class(request):
    student_id = request.GET.get('student_id')
    if student_id:
        student = Student.objects.get(id=student_id)
        return JsonResponse({"class_id": student.current_class.id, "class_name": student.current_class.name})
    return JsonResponse({"class_id": None, "class_name": ""})


class SearchStudents(View):
    def get(self, request):
        term = request.GET.get('term')
        students = Student.objects.filter(name__icontains=term)
        data = [{'id': student.id, 'text': student.name} for student in students]
        return JsonResponse(data, safe=False)


# ---------------------------
# Receipt Views
# ---------------------------
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
        context["show_receipt_button"] = True
        return context


class ReceiptUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Receipt
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]
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


# ---------------------------
# PDF Generation Views
# ---------------------------
def save_pdf(request):
    invoices = SalaryInvoice.objects.all()
    template_path = 'salary_pdf_template.html'
    context = {'invoices': invoices}
    template = get_template(template_path)
    html = template.render(context)
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


def generate_receipt(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    latest_receipt = invoice.receipt_set.latest('date_paid')
    context = {
        'invoice': invoice,
        'current_date': timezone.now(),
        'latest_receipt': latest_receipt,
    }
    return render(request, 'finance/receipt.html', context)


# ---------------------------
# Uniform Views
# ---------------------------
@login_required
def uniform_list(request):
    current_session = AcademicSession.objects.filter(current=True).first()
    selected_session_id = request.GET.get('session', current_session.id if current_session else None)
    selected_session = AcademicSession.objects.get(id=selected_session_id) if selected_session_id else None
    selected_class_id = request.GET.get('class', None)

    sessions = AcademicSession.objects.all()
    student_classes = StudentClass.objects.all()

    uniforms = Uniform.objects.filter(session=selected_session) if selected_session else Uniform.objects.none()
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

            uniform_items = Uniform.objects.filter(
                student=student, session=selected_session, student_class=uniform.student_class
            )

            for item in uniform_items:
                payable = item.uniform_type.price * (2 if item.quantity == "Jozi 2" else 1)
                total_payable += payable
                types_bought.append({
                    'uniform_type': item.uniform_type.name,
                    'quantity': item.quantity,
                    'uniform_id': item.pk
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
                'student_class_id': uniform.student_class.pk
            }
        else:
            # If the key already exists, re-calculate total_payable and update data
            uniform_items = Uniform.objects.filter(
                student=student, session=selected_session, student_class=uniform.student_class
            )
            types_bought = []
            total_payable = Decimal('0.00')
            for item in uniform_items:
                payable = item.uniform_type.price * (2 if item.quantity == "Jozi 2" else 1)
                total_payable += payable
                types_bought.append({
                    'uniform_type': item.uniform_type.name,
                    'quantity': item.quantity,
                    'uniform_id': item.pk
                })

            uniform_data[key]['total_payable'] = total_payable
            uniform_data[key]['balance'] = uniform_data[key]['total_paid'] - total_payable
            uniform_data[key]['types_bought'] = types_bought
            uniform_data[key]['student_class_id'] = uniform.student_class.pk

    return render(request, 'finance/uniform_list.html', {
        'uniform_data': uniform_data,
        'sessions': sessions,
        'selected_session': selected_session,
        'student_classes': student_classes,
        'selected_class_id': selected_class_id,
    })


@login_required
def uniform_create(request):
    if request.method == 'POST':
        formset = UniformFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    uniform = form.save(commit=False)
                    uniform.session = AcademicSession.objects.filter(current=True).first()
                    uniform.term = AcademicTerm.objects.filter(current=True).first()
                    uniform.save()
            return redirect('uniform_list')
    else:
        formset = UniformFormSet()

    student_class_map = {
        student.id: student.current_class.id for student in Student.objects.filter(current_status="active", completed=False)
    }
    uniform_type_prices = {
        uniform_type.id: float(uniform_type.price) for uniform_type in UniformType.objects.all()
    }

    context = {
        'formset': formset,
        'is_update': False,
        'student_class_map': student_class_map,
        'uniform_type_prices': uniform_type_prices,
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

    uniform_data = [
        {
            'uniform_type': uniform.get_uniform_type_display(),
            'quantity': uniform.quantity,
            'price': uniform.price
        }
        for uniform in uniforms
    ]

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
        'uniform_type_prices': uniform_type_prices
    })


def uniform_delete(request, pk):
    uniform = get_object_or_404(Uniform, pk=pk)
    if request.method == 'POST':
        uniform.delete()
        return redirect('uniform_list')
    return render(request, 'finance/uniform_confirm_delete.html', {'uniform': uniform})


def student_uniform_list(request):
    student_uniforms = StudentUniform.objects.all()
    return render(request, 'finance/student_uniform_list.html', {'student_uniforms': student_uniforms})


@login_required
def student_uniform_create(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    student_class_id = request.GET.get('class')
    student_class = get_object_or_404(StudentClass, pk=student_class_id)
    session = AcademicSession.objects.filter(current=True).first()
    term = AcademicTerm.objects.filter(current=True).first()

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
                student_uniform.amount += amount_to_add
            else:
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
        initial_data = {'student': student}
        if student_uniform:
            initial_data['amount'] = student_uniform.amount
        form = StudentUniformForm(initial=initial_data)

    return render(request, 'finance/student_uniform_form.html', {
        'form': form,
        'student': student,
        'student_class': student_class
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
        'session': session.name if session else '',
        'term': term.name if term else '',
        'student_class': student.current_class.name if student.current_class else '',
    }
    return JsonResponse(student_info)


# ---------------------------
# Dashboard View
# ---------------------------
class SelectLinkView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'finance/select_link.html'
    permission_required = 'finance.view_invoice'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_invoices = Invoice.objects.count()
        salary_invoices = SalaryInvoice.objects.count()
        expenditures_sum = Expenditure.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        context['total_invoices'] = total_invoices
        context['salary_invoices'] = salary_invoices
        context['expenditures'] = expenditures_sum
        return context


# ---------------------------
# UniformType Views
# ---------------------------
class UniformTypeListView(ListView):
    model = UniformType
    template_name = 'finance/uniformtype_list.html'
    context_object_name = 'uniform_types'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uniform_types = self.object_list
        uniform_type_data = [{
            'name': ut.name,
            'price_one': ut.price,
            'price_two': ut.price * 2,
            'id': ut.id,
        } for ut in uniform_types]
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


# ---------------------------
# Payment & Mpesa Integration
# (Adjust as needed if using Mpesa)
# ---------------------------
def initiate_payment(request):
    # Debugging line
    print(f"Current User: {request.user}")

    if request.method == 'POST':
        form = DynamicPaymentForm(request.POST, parent_user=request.user)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_type = form.cleaned_data['payment_type']
            student = getattr(request.user, 'student', None)

            if student:
                # NOTE: Uncomment and configure MpesaClient if using M-Pesa.
                # phone_number = '07620236662'
                # mpesa = MpesaClient()
                # response = mpesa.stk_push(
                #     phone_number,
                #     amount,
                #     account_reference="Test123",
                #     transaction_desc=f"Payment for {student}",
                #     callback_url=settings.MPESA_CALLBACK_URL
                # )

                # Fake response for demonstration:
                response = {'ResponseCode': '0', 'MerchantRequestID': 'some_id'}

                if response.get('ResponseCode') == '0':
                    payment = Payment.objects.create(
                        user=request.user,
                        amount=amount,
                        phone_number='07620236662',  # Hard-coded for example
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
                return redirect('parent_dashboard')
    else:
        form = DynamicPaymentForm(parent_user=request.user)

    return render(request, 'finance/initiate_payment.html', {'form': form})


@csrf_exempt
def mpesa_callback(request):
    data = request.body.decode('utf-8')
    # Example placeholder logic, adjust as per mpesa integration:
    # payment = MpesaPayment.process_mpesa_callback(data)
    # if payment.result_code == 0:
    #     payment_instance = Payment.objects.get(transaction_id=payment.transaction_id)
    #     payment_instance.status = 'completed'
    #     payment_instance.save()
    #     # Update related invoice/uniform payment
    # else:
    #     payment_instance.status = 'failed'
    #     payment_instance.save()

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

