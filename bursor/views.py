from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from accounts.models import AcademicUser, BursorUser
from apps.finance.models import Invoice, SalaryInvoice
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import TeacherUser
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from apps.finance.models import SalaryInvoice
from accounts.models import TeacherUser
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from accounts.models import TeacherUser
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, ExtractYear, ExtractMonth
from apps.finance.models import SalaryInvoice
from accounts.models import TeacherUser
from apps.corecode.models import StudentClass, Subject
from apps.result.models import Result
from collections import defaultdict
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass, Subject
from apps.students.models import Student
from apps.result.models import Result
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.corecode.models import StudentClass, Subject, AcademicSession, AcademicTerm, ExamType
from apps.students.models import Student
from apps.result.models import Result, StudentInfos
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from apps.result.models import Result, StudentInfos
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass
from apps.students.models import Student
from parents.models import InvoiceComments
from apps.finance.models import Invoice, InvoiceItem, Receipt
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, DeleteView, UpdateView, View
from .forms import BursorInvoiceItemFormset, BursorInvoiceReceiptFormSet
from apps.finance.models import Invoice, InvoiceItem, Receipt, SalaryInvoice
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.template.loader import render_to_string
from apps.students.models import Student
from apps.corecode.models import AcademicSession, AcademicTerm, Installment, StudentClass
from apps.staffs.models import Staff
from apps.finance.forms import InvoiceItemFormset, InvoiceReceiptFormSet
from event.models import Event
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.forms import ModelForm
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import FormView, CreateView, ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.db.models import Max
from expenditures.models import Category, Expenditure, ExpenditureInvoice
from collections import defaultdict
from expenditures.forms import ExpenditureInvoiceForm
import calendar
from library.models import Book, Stationery
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from school_properties.models import Property
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.db import transaction
#from .beem_service import send_sms, check_balance
from apps.students.models import Student
from apps.staffs.models import Staff
from sms.models import SentSMS
from sms.beem_service import send_sms, check_balance
from apps.finance.models import Uniform, StudentUniform
from apps.finance.forms import UniformForm, StudentUniformForm
from django.db import models
from apps.finance.forms import UniformTypeForm, UniformFormSet
from apps.finance.models import Uniform, UniformType
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import BursorAnswer
from accounts.models import ParentUser
from .forms import BursorAnswerForm
from accounts.forms import ParentUserCreationForm
from apps.corecode.models import AcademicSession

# accounts/views.py

from django.utils import timezone
from apps.staffs.models import StaffAttendance

from django.utils import timezone
from apps.staffs.models import StaffAttendance

from django.utils import timezone
from apps.staffs.models import StaffAttendance

from django.utils import timezone

def staff_sign_in(user):
    # Get the current date in the user's timezone
    today = timezone.localtime().date()

    # Set the start and end of the day based on the timezone
    start_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()), timezone.get_current_timezone())
    end_of_day = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()), timezone.get_current_timezone())

    # Check if there's already an attendance record for today
    attendance, created = StaffAttendance.objects.get_or_create(
        user=user,
        date=today  # Use date to ensure it checks by day and not time
    )
    
    # If the attendance was just created or the user wasn't marked present yet, update it
    if created or not attendance.is_present:
        attendance.is_present = True
        attendance.time_of_arrival = timezone.localtime()  # Use localtime to ensure it's in the correct timezone
        attendance.save()
    
    return attendance

from django.utils import timezone
from apps.staffs.models import StaffAttendance

"""
def should_show_sign_in_button(user):

    This function checks if the sign-in button should be shown.
    The button is shown if the current time is after 4:00 AM
    and the user has not signed in for the current day.

    current_time = timezone.localtime().time()  # Use localtime to ensure it's in the correct timezone
    sign_in_time_limit = timezone.datetime.strptime("04:00", "%H:%M").time()

    # Get today's attendance record based on the correct date and time
    today = timezone.localtime().date()
    attendance = StaffAttendance.objects.filter(user=user, date=today).first()

    # Show the sign-in button if the user hasn't signed in today and it's after 4:00 AM
    return not attendance or not attendance.is_present and current_time >= sign_in_time_limit
"""


def should_show_sign_in_button(user):
    """
    This function checks if the sign-in button should be shown.
    The button is shown if the current date has started 
    and the user has not signed in for the current day.
    """
    today = timezone.localtime().date()

    # Get today's attendance record based on the correct date
    attendance = StaffAttendance.objects.filter(user=user, date=today).first()

    # Show the sign-in button if it's a new day and the user hasn't signed in yet
    return not attendance or not attendance.is_present


from django.shortcuts import render

def bursor_staff_management_home(request):
    """
    View to render the home page for Bursor Staff Management
    with buttons for Bursor Details and Staff List.
    """
    return render(request, 'bursor/bursor_staff_management_home.html')

from django.shortcuts import render

def bursor_student_management_home(request):
    """
    View to render the home page for Bursor Student Management
    with buttons for managing student lists, inactive students, and alumni.
    """
    return render(request, 'bursor/bursor_student_management_home.html')

@login_required
def bursor_dashboard(request):
    staff = request.user.bursoruser.staff

    # Determine whether to show the sign-in button
    show_sign_in_button = should_show_sign_in_button(request.user)

    unsatisfied_comments = InvoiceComments.objects.filter(satisfied=False)

    context = {
        'staff': staff,
        'unsatisfied_comments': unsatisfied_comments,
        'new_comments_count': unsatisfied_comments.count(),
        'show_sign_in_button': show_sign_in_button,  # Pass this to the template
    }
    return render(request, 'bursor/bursor_dashboard.html', context)

@login_required
def mark_attendance(request):
    # Mark the attendance for the Bursor
    staff_sign_in(request.user)
    messages.success(request, "Attendance marked successfully.")
    return redirect('bursor_dashboard')

@login_required
def bursor_profile(request):
    return render(request, 'bursor/bursor_profile.html')

@login_required
def bursor_logout(request):
    logout(request)
    return redirect('login')

@login_required
def bursor_details(request):
    bursor_user = get_object_or_404(BursorUser, id=request.user.id)
    staff = bursor_user.staff

    context = {
        'object': staff
    }

    return render(request, 'bursor/bursor_details.html', context)

@login_required
def bursor_salary_invoices(request):
    bursor_user = get_object_or_404(BursorUser, id=request.user.id)
    staff = bursor_user.staff

    # Retrieve all salary invoices for the given staff
    invoices = SalaryInvoice.objects.filter(staff=staff).order_by('month')

    # Organize invoices by month and year
    invoices_by_month_year = invoices.annotate(month_year=TruncMonth('month')).values('month_year').annotate(
        total_gross_salary=Sum('gross_salary'),
        total_deductions=Sum('deductions'),
        total_net_salary=Sum('net_salary'),
        count=Count('id')
    ).order_by('-month_year')

    # Get unique years for the filter dropdown
    invoice_years = invoices.annotate(year=ExtractYear('month')).values_list('year', flat=True).distinct().order_by('year')

    context = {
        'invoices': invoices,
        'invoices_by_month_year': invoices_by_month_year,
        'invoice_years': invoice_years,
        'teacher_name': f"{staff.firstname} {staff.middle_name} {staff.surname}",
    }

    return render(request, 'bursor/bursor_salary_invoices.html', context)

@login_required
def bursor_class_list(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        return redirect('bursor_class_results', class_id=class_id)
    
    context = {
        'classes': classes
    }
    return render(request, 'bursor/bursor_class_list.html', context)

@login_required
def bursor_class_results(request, class_id):
    selected_class = get_object_or_404(StudentClass, id=class_id)
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    exams = ExamType.objects.all()
    subjects = Subject.objects.all()

    # Get the current session, term, and exam
    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    current_exam = ExamType.objects.filter(current=True).first()

    data = []

    for session in sessions:
        for term in terms:
            for exam in exams:
                # Retrieve results for the given class, session, term, and exam
                results = Result.objects.filter(
                    current_class=selected_class,
                    session=session,
                    term=term,
                    exam=exam
                ).select_related('student', 'subject')

                if results.exists():
                    session_term_exam_data = {
                        'session': session,
                        'term': term,
                        'exam': exam,
                        'results': [],
                        'subject_data': []
                    }

                    # Retrieve students who have results in this session, term, and exam
                    students = Student.objects.filter(
                        result__current_class=selected_class,
                        result__session=session,
                        result__term=term,
                        result__exam=exam
                    ).distinct()

                    for student in students:
                        student_results = results.filter(student=student)

                        if student_results.exists():
                            student_data = {
                                'student': student,
                                'student_class': selected_class,
                                'subjects': {},
                                'total': Decimal(0),
                                'overall_average': Decimal(0),
                                'overall_status': 'FAIL',
                                'position': None  # Position will be calculated later
                            }

                            total_score = Decimal(0)
                            total_subjects = 0

                            for subject in subjects:
                                subject_result = student_results.filter(subject=subject).first()
                                if subject_result:
                                    student_data['subjects'][subject] = {
                                        'test_score': subject_result.test_score,
                                        'exam_score': subject_result.exam_score,
                                        'average': subject_result.average
                                    }
                                    total_score += subject_result.average if subject_result.average else Decimal(0)
                                    total_subjects += 1
                                else:
                                    student_data['subjects'][subject] = {
                                        'test_score': None,
                                        'exam_score': None,
                                        'average': None
                                    }

                            if total_subjects > 0:
                                student_data['total'] = total_score
                                student_data['overall_average'] = total_score / total_subjects
                                student_data['overall_status'] = 'PASS' if student_data['overall_average'] >= Decimal(25) else 'FAIL'

                            session_term_exam_data['results'].append(student_data)

                    # Sort the results by overall average in descending order
                    session_term_exam_data['results'].sort(key=lambda x: x['overall_average'], reverse=True)

                    # Calculate positions with tie handling
                    current_position = 1
                    i = 0

                    while i < len(session_term_exam_data['results']):
                        tie_group = [session_term_exam_data['results'][i]]
                        j = i + 1

                        while j < len(session_term_exam_data['results']) and session_term_exam_data['results'][j]['overall_average'] == session_term_exam_data['results'][i]['overall_average']:
                            tie_group.append(session_term_exam_data['results'][j])
                            j += 1

                        # Calculate average position for the tie group
                        if len(tie_group) > 1:
                            average_position = current_position + 0.5
                            for result in tie_group:
                                result['position'] = average_position
                        else:
                            tie_group[0]['position'] = current_position

                        # Move to the next group
                        current_position += len(tie_group)
                        i = j

                    # Calculate subject data
                    for subject in subjects:
                        subject_results = results.filter(subject=subject)
                        if subject_results.exists():
                            total_subject_average = sum(result.average for result in subject_results)
                            total_students = subject_results.count()
                            subject_average = total_subject_average / total_students

                            if subject_average >= Decimal(41):
                                subject_grade = 'A'
                            elif subject_average >= Decimal(30):
                                subject_grade = 'B'
                            elif subject_average >= Decimal(25):
                                subject_grade = 'C'
                            elif subject_average >= Decimal(15):
                                subject_grade = 'D'
                            else:
                                subject_grade = 'F'

                            subject_gpa = (subject_average / Decimal(50)) * Decimal(4.0)

                            session_term_exam_data['subject_data'].append({
                                'subject': subject,
                                'average': subject_average,
                                'grade': subject_grade,
                                'gpa': round(subject_gpa, 3)  # Round to 3 decimal places
                            })

                    # Sort the subjects by average in descending order
                    session_term_exam_data['subject_data'].sort(key=lambda x: x['average'], reverse=True)

                    data.append(session_term_exam_data)

    context = {
        'selected_class': selected_class,
        'data': data,
        'subjects': subjects,
        'sessions': sessions,
        'terms': terms,
        'exams': exams,
        'current_session': current_session,
        'current_term': current_term,
        'current_exam': current_exam,
    }
    return render(request, 'bursor/bursor_class_results.html', context)

@login_required
def bursor_all_class_list(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        return redirect('bursor_all_class_results', class_id=class_id)
    
    context = {
        'classes': classes
    }
    return render(request, 'bursor/bursor_all_class_list.html', context)

@login_required
def bursor_all_class_results(request, class_id):
    selected_class = get_object_or_404(StudentClass, id=class_id)
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    exams = ExamType.objects.all()
    subjects = Subject.objects.all()

    # Get the current session, term, and exam
    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    current_exam = ExamType.objects.filter(current=True).first()

    data = []

    for session in sessions:
        for term in terms:
            for exam in exams:
                # Retrieve results for the given class, session, term, and exam
                results = Result.objects.filter(
                    current_class=selected_class,
                    session=session,
                    term=term,
                    exam=exam
                ).select_related('student', 'subject')

                if results.exists():
                    session_term_exam_data = {
                        'session': session,
                        'term': term,
                        'exam': exam,
                        'results': [],
                        'subject_data': []
                    }

                    # Retrieve students who have results in this session, term, and exam
                    students = Student.objects.filter(
                        result__current_class=selected_class,
                        result__session=session,
                        result__term=term,
                        result__exam=exam
                    ).distinct()

                    for student in students:
                        student_results = results.filter(student=student)

                        if student_results.exists():
                            student_data = {
                                'student': student,
                                'student_class': selected_class,
                                'subjects': {},
                                'total': Decimal(0),
                                'overall_average': Decimal(0),
                                'overall_status': 'FAIL',
                                'position': None  # Position will be calculated later
                            }

                            total_score = Decimal(0)
                            total_subjects = 0

                            for subject in subjects:
                                subject_result = student_results.filter(subject=subject).first()
                                if subject_result:
                                    student_data['subjects'][subject] = {
                                        'test_score': subject_result.test_score,
                                        'exam_score': subject_result.exam_score,
                                        'average': subject_result.average
                                    }
                                    total_score += subject_result.average if subject_result.average else Decimal(0)
                                    total_subjects += 1
                                else:
                                    student_data['subjects'][subject] = {
                                        'test_score': None,
                                        'exam_score': None,
                                        'average': None
                                    }

                            if total_subjects > 0:
                                student_data['total'] = total_score
                                student_data['overall_average'] = total_score / total_subjects
                                student_data['overall_status'] = 'PASS' if student_data['overall_average'] >= Decimal(25) else 'FAIL'

                            session_term_exam_data['results'].append(student_data)

                    # Sort the results by overall average in descending order
                    session_term_exam_data['results'].sort(key=lambda x: x['overall_average'], reverse=True)

                    # Calculate positions with tie handling
                    current_position = 1
                    i = 0

                    while i < len(session_term_exam_data['results']):
                        tie_group = [session_term_exam_data['results'][i]]
                        j = i + 1

                        while j < len(session_term_exam_data['results']) and session_term_exam_data['results'][j]['overall_average'] == session_term_exam_data['results'][i]['overall_average']:
                            tie_group.append(session_term_exam_data['results'][j])
                            j += 1

                        # Calculate average position for the tie group
                        if len(tie_group) > 1:
                            average_position = current_position + 0.5
                            for result in tie_group:
                                result['position'] = average_position
                        else:
                            tie_group[0]['position'] = current_position

                        # Move to the next group
                        current_position += len(tie_group)
                        i = j

                    # Calculate subject data
                    for subject in subjects:
                        subject_results = results.filter(subject=subject)
                        if subject_results.exists():
                            total_subject_average = sum(result.average for result in subject_results)
                            total_students = subject_results.count()
                            subject_average = total_subject_average / total_students

                            if subject_average >= Decimal(41):
                                subject_grade = 'A'
                            elif subject_average >= Decimal(30):
                                subject_grade = 'B'
                            elif subject_average >= Decimal(25):
                                subject_grade = 'C'
                            elif subject_average >= Decimal(15):
                                subject_grade = 'D'
                            else:
                                subject_grade = 'F'

                            subject_gpa = (subject_average / Decimal(50)) * Decimal(4.0)

                            session_term_exam_data['subject_data'].append({
                                'subject': subject,
                                'average': subject_average,
                                'grade': subject_grade,
                                'gpa': round(subject_gpa, 3)  # Round to 3 decimal places
                            })

                    # Sort the subjects by average in descending order
                    session_term_exam_data['subject_data'].sort(key=lambda x: x['average'], reverse=True)

                    data.append(session_term_exam_data)

    context = {
        'selected_class': selected_class,
        'data': data,
        'subjects': subjects,
        'sessions': sessions,
        'terms': terms,
        'exams': exams,
        'current_session': current_session,
        'current_term': current_term,
        'current_exam': current_exam,
    }
    return render(request, 'bursor/bursor_all_class_results.html', context)

class BursorInvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'bursor/bursor_invoice_list.html'
    context_object_name = 'invoices'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = AcademicSession.objects.all()
        context['installments'] = Installment.objects.all()
        context['classes'] = StudentClass.objects.all()
        return context

class BursorInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    fields = "__all__"
    template_name = "bursor/bursor_invoice_form.html"
    success_url = reverse_lazy("bursor-invoice-list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter students who are active and have not completed school
        form.fields['student'].queryset = Student.objects.filter(current_status="active", completed=False)
        return form

    def get_context_data(self, **kwargs):
        context = super(BursorInvoiceCreateView, self).get_context_data(**kwargs)
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

class BursorInvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    template_name = "bursor/bursor_invoice_form.html"  # Set your custom template name here
    fields = ["student", "session", "installment", "class_for", "balance_from_previous_install"]

    def get_context_data(self, **kwargs):
        context = super(BursorInvoiceUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["receipts"] = InvoiceReceiptFormSet(self.request.POST, instance=self.object)
            context["items"] = InvoiceItemFormset(self.request.POST, instance=self.object)
        else:
            context["receipts"] = InvoiceReceiptFormSet(instance=self.object)
            context["items"] = BursorInvoiceItemFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["receipts"]
        itemsformset = context["items"]
        if form.is_valid() and formset.is_valid() and itemsformset.is_valid():
            form.save()
            formset.save()
            itemsformset.save()
            messages.success(self.request, "Invoice updated successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('bursor-invoice-list')



class BursorInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    fields = "__all__"
    template_name = "bursor/bursor_invoice_detail.html"  # Set your custom template name here

    def get_context_data(self, **kwargs):
        context = super(BursorInvoiceDetailView, self).get_context_data(**kwargs)
        context["receipts"] = Receipt.objects.filter(invoice=self.object)
        context["items"] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class BursorSearchStudents(View):
    def get(self, request):
        term = request.GET.get('term')
        students = Student.objects.filter(name__icontains=term)
        data = [{'id': student.id, 'text': student.name} for student in students]
        return JsonResponse(data, safe=False)

class BursorInvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = "bursor/bursor_invoice_confirm_delete.html"  # Set your custom template name here
    success_url = reverse_lazy("bursor-invoice-list")

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, "Invoice deleted successfully!")
        return response

"""
class BursorReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    template_name = "bursor/bursor_receipt_form.html"  # Set your custom template name here
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("bursor-invoice-list")

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
            obj.invoice = invoice
            obj.save()
            return super().form_valid(form)
        except Exception as e:
            # Handle any exceptions here
            return HttpResponseRedirect(reverse_lazy("bursor-invoice-list"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
        context["invoice"] = invoice
        return context
"""

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

class BursorReceiptCreateView(LoginRequiredMixin, CreateView):
    model = Receipt
    template_name = "bursor/bursor_receipt_form.html"  # Set your custom template name here
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("bursor-invoice-list")

    def form_valid(self, form):
        try:
            obj = form.save(commit=False)
            invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
            obj.invoice = invoice
            obj.save()
            # Redirect to the receipt detail view after saving the receipt
            return HttpResponseRedirect(reverse('bursor-receipt-detail', args=[obj.pk]))
        except Exception as e:
            # Handle any exceptions here
            return HttpResponseRedirect(reverse_lazy("bursor-invoice-list"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, pk=self.request.GET.get("invoice"))
        context["invoice"] = invoice
        return context

from django.views.generic import DetailView
from apps.corecode.models import Signature

class BursorReceiptDetailView(LoginRequiredMixin, DetailView):
    model = Receipt
    template_name = "bursor/bursor_receipt_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the invoice associated with the receipt
        receipt = self.get_object()
        invoice = receipt.invoice
        context["invoice"] = invoice

        # Retrieve the Headmaster's signature
        headmaster_signature = Signature.objects.filter(name="Headmaster's signature").first()
        context["headmaster_signature"] = headmaster_signature

        # Retrieve the Bursor's signature
        bursor_signature = Signature.objects.filter(name="Bursor's signature").first()
        context["bursor_signature"] = bursor_signature

        return context


class BursorReceiptUpdateView(LoginRequiredMixin, UpdateView):
    model = Receipt
    template_name = "bursor/bursor_receipt_form.html"  # Set your custom template name here
    fields = ["amount_paid", "date_paid", "comment", "payment_method"]  # Include the payment_method field
    success_url = reverse_lazy("invoice-list")

class BursorReceiptDeleteView(LoginRequiredMixin, DeleteView):
    model = Receipt
    template_name = "bursor/bursor_invoice_confirm_delete.html"  # Set your custom template name here
    success_url = reverse_lazy("bursor-invoice-list")

@login_required
def bursor_bulk_invoice(request):
    return render(request, "bursor/bursor_bulk_invoice.html")

class BursorEventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'bursor/bursor_event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        # Get the current session and term
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)

        # Filter events based on the current session and term
        queryset = super().get_queryset().filter(session=current_session, term=current_term)

        # Modify the queryset to order events by the creation date
        queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for event in context['events']:
            event.time_since_creation = self.get_time_since_creation(event.created_at)
        return context

    def get_time_since_creation(self, created_at):
        time_since = timezone.now() - created_at
        seconds = abs(time_since.total_seconds())
        if seconds < 60:
            return f"{int(seconds)} seconds"
        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)} minutes"
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)} hours"
        days = hours / 24
        if days < 365:
            return f"{int(days)} days"
        return "Over a year ago"
    
class BursorStudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "bursor/bursor_student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return Student.objects.filter(current_status="active", completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        return context


class BursorInactiveStudentsView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "bursor/bursor_inactive_student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        return Student.objects.filter(current_status="inactive", completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        context['staff_list'] = Staff.objects.filter(current_status="inactive")
        return context

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

class BursorCompletedStudentsView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "bursor/bursor_completed_student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        # Filter students who are inactive and completed or active and completed
        return Student.objects.filter(completed=True).filter(
            models.Q(current_status="inactive") | models.Q(current_status="active")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add student classes to the context for filtering options
        context['student_classes'] = StudentClass.objects.all()
        return context

class BursorCompletedStudentDetailView(DetailView):
    model = Student
    template_name = "bursor/bursor_completed_student_detail.html"
    context_object_name = "object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = Invoice.objects.filter(student=self.object)

        # Group results and student infos by session, term, and exam type
        results = Result.objects.filter(student=self.object).order_by('session', 'term', 'exam')
        student_infos = StudentInfos.objects.filter(student=self.object).order_by('session', 'term', 'exam', '-id')

        grouped_data = {}

        for result in results:
            session = result.session.name
            term = result.term.name
            exam = result.exam.name
            if session not in grouped_data:
                grouped_data[session] = {}
            if term not in grouped_data[session]:
                grouped_data[session][term] = {}
            if exam not in grouped_data[session][term]:
                grouped_data[session][term][exam] = {'results': [], 'infos': []}
            grouped_data[session][term][exam]['results'].append(result)

        for info in student_infos:
            session = info.session.name
            term = info.term.name
            exam = info.exam.name
            if session not in grouped_data:
                grouped_data[session] = {}
            if term not in grouped_data[session]:
                grouped_data[session][term] = {}
            if exam not in grouped_data[session][term]:
                grouped_data[session][term][exam] = {'results': [], 'infos': []}
            # Only add the latest info for each session, term, and exam
            if not grouped_data[session][term][exam]['infos']:
                grouped_data[session][term][exam]['infos'].append(info)

        # Calculate totals and averages
        for session, terms in grouped_data.items():
            for term, exams in terms.items():
                for exam, data in exams.items():
                    total = sum(result.average for result in data['results'])
                    subject_count = len(data['results'])
                    total_marks = subject_count * 50
                    student_average = total / subject_count if subject_count > 0 else 0

                    # Calculate position
                    student_class = self.object.current_class
                    students_in_class = Result.objects.filter(current_class=student_class, session__name=session, term__name=term, exam__name=exam).values('student').distinct()
                    total_students = students_in_class.count()

                    all_averages = [sum(Result.objects.filter(student=student['student'], session__name=session, term__name=term, exam__name=exam).values_list('average', flat=True)) for student in students_in_class]
                    all_averages.sort(reverse=True)
                    student_position = all_averages.index(total) + 1 if total in all_averages else None

                    data['total'] = total
                    data['total_marks'] = total_marks
                    data['student_average'] = student_average
                    data['student_position'] = student_position
                    data['total_students'] = total_students

        context['grouped_data'] = grouped_data
        return context
    
class BursorStudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "bursor/bursor_student_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)
        return context

class BursorExpenditureInvoiceListView(LoginRequiredMixin, ListView):
    model = ExpenditureInvoice
    template_name = 'bursor/bursor_expenditure_invoice_list.html'
    context_object_name = 'invoices'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=Sum('initial_balance'))['total'] or 0

        # Calculate total general amount
        total_general_amount = Expenditure.objects.aggregate(total=Sum('amount'))['total'] or 0

        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount

        # Add data to the context
        context['total_initial_balance'] = total_initial_balance
        context['total_general_amount'] = total_general_amount
        context['reminder_balance'] = reminder_balance

        return context


class BursorExpenditureInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = ExpenditureInvoice
    form_class = ExpenditureInvoiceForm  # Specify the form class
    template_name = 'bursor/bursor_expenditure_invoice_form.html'  # Replace this with the actual path to your template
    success_url = reverse_lazy('bursor-expenditure-invoice-list')  # Redirect to the expenditure invoice list URL after successful form submission

class BursorExpenditureInvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = ExpenditureInvoice
    template_name = 'bursor/bursor_expenditure_invoice_update.html'
    fields = ['date', 'depositor_name', 'initial_balance']  # Remove 'total_amount'
    success_url = reverse_lazy('bursor-expenditure-invoice-list')

class BursorExpenditureInvoiceDetailView(LoginRequiredMixin, DetailView):
    model = ExpenditureInvoice
    template_name = 'bursor/bursor_expenditure_invoice_detail.html'
    context_object_name = 'invoice'

class BursorExpenditureInvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = ExpenditureInvoice
    template_name = 'bursor/bursor_expenditure_invoice_confirm_delete.html'
    success_url = reverse_lazy('bursor-expenditure-invoice-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = self.get_object()
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(ExpenditureInvoice, pk=self.kwargs['pk'])


class BursorExpenditureEditView(LoginRequiredMixin, UpdateView):
    model = Expenditure
    fields = ['category', 'item_name', 'amount', 'date', 'description', 'quantity', 'attachment']
    template_name = 'bursor/bursor_edit_expenditure.html'

    def get_success_url(self):
        return reverse_lazy('bursor_category_detail', kwargs={'pk': self.object.category.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Include categories in context
        return context

class BursorExpenditureCreateView(LoginRequiredMixin, CreateView):
    model = Expenditure
    template_name = 'bursor/bursor_expenditure_form.html'
    fields = ['category', 'item_name', 'amount', 'date', 'description', 'quantity', 'attachment']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        # Save the form data
        self.object = form.save()

        # Add a success message if you want
        # messages.success(self.request, "Expenditure created successfully.")

        # Redirect to the expenditure list
        return HttpResponseRedirect(reverse_lazy('bursor_expenditure_list'))


class BursorExpenditureListView(LoginRequiredMixin, ListView):
    model = Expenditure
    template_name = 'bursor/bursor_expenditure_list.html'
    context_object_name = 'expenditures'

    def get_queryset(self):
        # Retrieve all expenditures
        expenditures = Expenditure.objects.select_related('category').order_by('-date')

        # Filter by search category if provided
        search_category = self.request.GET.get('search_category')
        if search_category:
            expenditures = expenditures.filter(category__name__icontains=search_category)

        # Filter by date or month if provided
        search_date = self.request.GET.get('search_date')
        if search_date:
            # Parse search_date as a date object
            search_date = timezone.datetime.strptime(search_date, '%Y-%m-%d').date()
            # Filter expenditures by the date
            expenditures = expenditures.filter(date=search_date)
        else:
            # Filter by month if provided
            search_month = self.request.GET.get('search_month')
            if search_month:
                # Parse search_month as a date object
                search_month = timezone.datetime.strptime(search_month, '%Y-%m').date()
                # Filter expenditures by the month
                expenditures = expenditures.filter(date__year=search_month.year, date__month=search_month.month)

        return expenditures

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Organize expenditures by category
        category_tables = {}
        for expenditure in context['expenditures']:
            category_name = expenditure.category.name
            if category_name not in category_tables:
                category_tables[category_name] = {'category_name': category_name, 'rows': [], 'total_amount': 0}
            category_tables[category_name]['rows'].append(expenditure)
            category_tables[category_name]['total_amount'] += expenditure.amount  # Accumulate total amount

        # Debug output for expenditure attachments
        for expenditure in context['expenditures']:
            print("Expenditure Attachment:", expenditure.attachment)

        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=Sum('initial_balance'))['total'] or 0

        # Calculate total general amount
        total_general_amount = sum([expenditure.amount for expenditure in context['expenditures']])

        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount

        # Add data to the context
        context['expenditures'] = list(category_tables.values())
        context['total_general_amount'] = total_general_amount
        context['total_initial_balance'] = total_initial_balance
        context['reminder_balance'] = reminder_balance

        return context


class BursorExpenditureDeleteView(LoginRequiredMixin, DeleteView):
    model = Expenditure
    success_url = reverse_lazy('bursor_expenditure_list')
    template_name = 'bursor/bursor_expenditure_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        # Get the expenditure object to be deleted
        expenditure = self.get_object()

        # Calculate the amount to be deducted from the total balance
        amount_to_deduct = expenditure.amount

        # Delete the expenditure
        response = super().delete(request, *args, **kwargs)

        # Calculate total initial balance
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=models.Sum('initial_balance'))['total'] or 0

        # Calculate total general amount
        total_general_amount = Expenditure.objects.aggregate(total=models.Sum('amount'))['total'] or 0

        # Calculate reminder balance
        reminder_balance = total_initial_balance - total_general_amount

        # Optionally, update the total balance or perform any additional actions

        # Display a success message
        messages.success(request, 'Expenditure deleted successfully.')

        return response


class BursorExpenditureDetailView(LoginRequiredMixin, DetailView):
    model = Expenditure
    template_name = 'bursor/bursor_expenditure_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BursorCategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'bursor/bursor_category_create.html'
    success_url = reverse_lazy('bursor_category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category created successfully.")
        return super().form_valid(form)


class BursorCategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'bursor/bursor_category_list.html'


class BursorCategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'bursor/bursor_category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        # Calculate total expenditure amount for the category
        total_expenditure_amount = Expenditure.objects.filter(category=category).aggregate(total=Sum('amount'))['total'] or 0

        # Calculate total initial balance from all expenditure invoices
        total_initial_balance = ExpenditureInvoice.objects.aggregate(total=Sum('initial_balance'))['total'] or 0

        # Calculate total balance
        total_balance = total_initial_balance - total_expenditure_amount

        # Add the calculated values to the context
        context['expenditures'] = category.expenditure_set.all()
        context['total_expenditure_amount'] = total_expenditure_amount
        context['total_initial_balance'] = total_initial_balance
        context['total_balance'] = total_balance

        return context

class BursorCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'bursor/bursor_category_update.html'  # Create a template for category update
    success_url = reverse_lazy('bursor_category_list')

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully.")
        return super().form_valid(form)

class BursorCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'bursor/bursor_category_confirm_delete.html'  # Create a template for category delete
    success_url = reverse_lazy('bursor_category_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully.")
        return super().delete(request, *args, **kwargs)

class BursorViewAvailableBooksView(View):
    def get(self, request):
        books_by_class = Book.objects.all().order_by('student_class')
        grouped_books = {}
        for book in books_by_class:
            if book.student_class.name not in grouped_books:
                grouped_books[book.student_class.name] = []
            grouped_books[book.student_class.name].append(book)
        return render(request, 'bursor/bursor_view_books.html', {'grouped_books': grouped_books})

class BursorBookDetailView(View):
    def get(self, request, book_id):
        book = Book.objects.get(pk=book_id)
        return render(request, 'bursor/bursor_book_details.html', {'book': book})
    
class BursorStationeryListView(View, LoginRequiredMixin):

    def get(self, request):
        stationeries = Stationery.objects.all().order_by('-date_buyed')  # Order by date_buyed descending
        total_quantity = stationeries.aggregate(total_quantity=Sum('quantity'))['total_quantity']

        # Group stationeries by month and year, handling None date_buyed
        grouped_stationeries = {}
        for key, group in groupby(stationeries, key=lambda x: x.date_buyed.strftime('%Y-%m') if x.date_buyed else 'No Date'):
            if key != 'No Date':
                year_month = datetime.strptime(key, '%Y-%m')
            else:
                year_month = key
            grouped_stationeries[year_month] = list(group)

        # Sort grouped stationeries by month in descending order
        sorted_grouped_stationeries = dict(sorted(grouped_stationeries.items(), key=lambda x: (x[0] != 'No Date', x[0]), reverse=True))

        return render(request, 'bursor/bursor_stationery_list.html', {
            'grouped_stationeries': sorted_grouped_stationeries,
            'total_quantity': total_quantity
        })

class BursorStationeryDetailView(View):
    def get(self, request, stationery_id):
        stationery = get_object_or_404(Stationery, pk=stationery_id)
        return render(request, 'bursor/bursor_stationery_details.html', {'stationery': stationery})
    
@login_required
def bursor_property_list(request):
    current_session = AcademicSession.objects.filter(current=True).first()
    properties = Property.objects.filter(session=current_session)
    return render(request, 'bursor/bursor_property_list.html', {'properties': properties})

@login_required
def bursor_property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'bursor/bursor_property_details.html', {'property': property})


class BursorSendSMSFormView(LoginRequiredMixin, View):

    def get(self, request):
        students = Student.objects.filter(current_status="active", completed=False)
        staff = Staff.objects.filter(current_status="active")
        classes = StudentClass.objects.all()  # Fetch all classes
        return render(request, 'bursor/bursor_send_sms.html', {
            'students': students,
            'staff': staff,
            'classes': classes
        })

    def post(self, request):
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type')
        recipients = []

        if recipient_type == 'students':
            student_recipients = request.POST.getlist('student_recipients')
            for student_id in student_recipients:
                student = Student.objects.get(id=student_id)
                if student.father_mobile_number:
                    recipients.append({
                        "dest_addr": student.father_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
                if student.mother_mobile_number:
                    recipients.append({
                        "dest_addr": student.mother_mobile_number,
                        "first_name": student.firstname,
                        "last_name": student.surname
                    })
        elif recipient_type == 'staff':
            staff_recipients = request.POST.getlist('staff_recipients')
            recipients = [
                {
                    "dest_addr": staff_member.mobile_number,
                    "first_name": staff_member.firstname,
                    "last_name": staff_member.surname
                } for staff_member in Staff.objects.filter(mobile_number__in=staff_recipients)
            ]

        if not recipients:
            messages.error(request, 'No recipients selected.')
            # Ensure only active and non-completed students and active staff are reloaded in the form
            return render(request, 'bursor/bursor_send_sms.html', {
                'students': Student.objects.filter(current_status="active", completed=False),
                'staff': Staff.objects.filter(current_status="active"),
                'classes': StudentClass.objects.all()
            })

        try:
            response = send_sms(message, recipients)
            if response.get('error'):
                messages.error(request, 'Failed to send SMS: ' + response['error'])
            else:
                messages.success(request, 'SMS sent successfully!')
            return redirect('bursor_send_sms_form')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('bursor_send_sms_form')

class BursorSMSHistoryView(LoginRequiredMixin, View):

    def get(self, request):
        # Filter to get only sent messages
        messages_query = SentSMS.objects.filter(status='Sent').order_by('-sent_date')

        # Use a set to track unique messages and filter out duplicates
        seen = set()
        unique_messages = []
        for message in messages_query:
            identifier = (
                message.status,
                message.sent_date,
                message.first_name,
                message.last_name,
                message.dest_addr,
                message.message
            )
            if identifier not in seen:
                seen.add(identifier)
                unique_messages.append(message)

        total_sms = len(unique_messages)

        context = {
            'messages': unique_messages,
            'total_sms': total_sms
        }
        return render(request, 'bursor/bursor_sms_history.html', context)

    def post(self, request):
        sms_ids = request.POST.getlist('sms_ids')
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            messages.error(request, 'No messages selected for deletion.')
        return redirect('bursor_sms_history')


class BursorCheckBalanceView(View):
    def get(self, request):
        try:
            response = check_balance()
            if "error" in response:
                return render(request, 'bursor/bursor_check_balance.html', {'error': response['error']})
            return render(request, 'bursor/bursor_check_balance.html', {'balance': response.get('data', {}).get('credit_balance', 'N/A')})
        except Exception as e:
            return render(request, 'bursor/bursor_check_balance.html', {'error': str(e)})

@method_decorator(require_POST, name='dispatch')
class BursorDeleteSMSView(View):
    def post(self, request):
        sms_ids = request.POST.getlist('sms_ids')
        if sms_ids:
            with transaction.atomic():
                deleted_count, _ = SentSMS.objects.filter(id__in=sms_ids).delete()
                messages.success(request, f'Successfully deleted {deleted_count} messages.')
        else:
            messages.error(request, 'No messages selected for deletion.')
        return redirect('bursor_sms_history')

class BursorStaffListView(LoginRequiredMixin, ListView):
    model = Staff
    template_name = 'bursor/bursor_staff_list.html'
    context_object_name = 'staff_list'

    def get_queryset(self):
        return Staff.objects.filter(current_status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_male'] = Staff.objects.filter(gender='male').count()
        context['total_female'] = Staff.objects.filter(gender='female').count()
        context['overall_total'] = Staff.objects.count()
        return context


@login_required
def bursor_create_parent_user(request):
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST)
        if form.is_valid():
            parent_user = form.save()
            # Send SMS
            student = parent_user.student
            message = (
                f"Habari ndugu mzazi wa {student.firstname} {student.middle_name} {student.surname}, "
                f"pokea taarifa hizi za kukuwezesha kuingia kwenye mfumo wa shule, "
                f"username: {parent_user.username}, password: {request.POST.get('password1')}, "
                "usifute meseji hii kwa msaada piga 0744394080."
            )
            recipients = []

            # Add father's mobile number if it exists
            if student.father_mobile_number:
                recipients.append({
                    "dest_addr": student.father_mobile_number,
                    "first_name": parent_user.parent_first_name,
                    "last_name": parent_user.parent_last_name
                })

            # Add mother's mobile number if it exists
            if student.mother_mobile_number:
                recipients.append({
                    "dest_addr": student.mother_mobile_number,
                    "first_name": parent_user.parent_first_name,
                    "last_name": parent_user.parent_last_name
                })

            try:
                send_sms(message, recipients)
                messages.success(request, 'Parent user created successfully, and SMS has been sent.')
            except Exception as e:
                messages.error(request, f'Parent user created, but SMS sending failed: {e}')

            return redirect('bursor_parent_user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ParentUserCreationForm()
    return render(request, 'bursor/create_parent_user.html', {'form': form})

@login_required
def bursor_parent_user_list(request):
    parent_users = ParentUser.objects.all()
    return render(request, 'bursor/parent_user_list.html', {'parent_users': parent_users})

@login_required
def bursor_update_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        form = ParentUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parent user updated successfully.')
            return redirect('bursor_parent_user_list')
    else:
        form = ParentUserCreationForm(instance=user)
    return render(request, 'bursor/update_user.html', {'form': form, 'user_type': 'Parent'})

@login_required
def bursor_delete_parent_user(request, pk):
    user = get_object_or_404(ParentUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Parent user deleted successfully.')
        return redirect('bursor_parent_user_list')
    return render(request, 'accounts/delete_parent_user.html', {'user': user})

@login_required
def bursor_uniform_list(request):
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

    return render(request, 'bursor/uniform_list.html', {
        'uniform_data': uniform_data,
        'sessions': sessions,
        'selected_session': selected_session,
        'student_classes': student_classes,  # Pass the classes to the template
        'selected_class_id': selected_class_id,  # Pass the selected class ID to the template
    })

@login_required
def bursor_uniform_create(request):
    if request.method == 'POST':
        formset = UniformFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # Check if the form has data
                    uniform = form.save(commit=False)
                    uniform.session = AcademicSession.objects.filter(current=True).first()
                    uniform.term = AcademicTerm.objects.filter(current=True).first()
                    uniform.save()
            return redirect('bursor_uniform_list')
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

    return render(request, 'bursor/uniform_form.html', context)

@login_required
def bursor_uniform_detail(request, student_id):
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

    return render(request, 'bursor/uniform_detail.html', context)

def bursor_uniform_update(request, pk):
    uniform = get_object_or_404(Uniform, pk=pk)

    # Prepare the uniform type prices
    uniform_type_prices = {ut.id: str(ut.price) for ut in UniformType.objects.all()}

    if request.method == 'POST':
        form = UniformForm(request.POST, instance=uniform)
        if form.is_valid():
            form.save()
            return redirect('bursor_uniform_list')
    else:
        form = UniformForm(instance=uniform)

    return render(request, 'bursor/uniform_update.html', {
        'form': form,
        'uniform_type_prices': uniform_type_prices  # Pass the uniform type prices to the template
    })

def bursor_uniform_delete(request, pk):
    uniform = get_object_or_404(Uniform, pk=pk)
    if request.method == 'POST':
        uniform.delete()
        return redirect('bursor_uniform_list')
    return render(request, 'bursor/uniform_confirm_delete.html', {'uniform': uniform})

# StudentUniform views
def bursor_student_uniform_list(request):
    student_uniforms = StudentUniform.objects.all()
    return render(request, 'bursor/student_uniform_list.html', {'student_uniforms': student_uniforms})

@login_required
def bursor_student_uniform_create(request, student_id):
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
            return redirect('bursor_uniform_list')
    else:
        # If the record exists, initialize the form with the current amount
        initial_data = {'student': student}
        if student_uniform:
            initial_data['amount'] = student_uniform.amount

        form = StudentUniformForm(initial=initial_data)

    return render(request, 'bursor/student_uniform_form.html', {
        'form': form,
        'student': student,
        'student_class': student_class  # Pass the student_class to the template
    })

@login_required
def bursor_student_uniform_update(request, pk):
    student_uniform = get_object_or_404(StudentUniform, pk=pk)
    if request.method == 'POST':
        form = StudentUniformForm(request.POST, instance=student_uniform)
        if form.is_valid():
            form.save()
            return redirect('bursor_uniform_list')
    else:
        form = StudentUniformForm(instance=student_uniform)
    return render(request, 'bursor/student_uniform_form.html', {'form': form})

def bursor_student_uniform_delete(request, pk):
    student_uniform = get_object_or_404(StudentUniform, pk=pk)
    if request.method == 'POST':
        student_uniform.delete()
        return redirect('bursor_student_uniform_list')
    return render(request, 'bursor/student_uniform_confirm_delete.html', {'student_uniform': student_uniform})

class BursorUniformTypeListView(ListView):
    model = UniformType
    template_name = 'bursor/uniformtype_list.html'
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

class BursorUniformTypeCreateView(CreateView):
    model = UniformType
    form_class = UniformTypeForm
    template_name = 'bursor/uniformtype_form.html'
    success_url = reverse_lazy('bursoruniformtype_list')

class BursorUniformTypeUpdateView(UpdateView):
    model = UniformType
    form_class = UniformTypeForm
    template_name = 'bursor/uniformtype_form.html'
    success_url = reverse_lazy('bursoruniformtype_list')

class BursorUniformTypeDeleteView(DeleteView):
    model = UniformType
    template_name = 'bursor/uniformtype_confirm_delete.html'
    success_url = reverse_lazy('bursoruniformtype_list')

@login_required
def bursor_get_uniform_price(request):
    uniform_type_name = request.GET.get('type')
    try:
        uniform_type = UniformType.objects.get(name=uniform_type_name)
        return JsonResponse({'price': uniform_type.price})
    except UniformType.DoesNotExist:
        return JsonResponse({'price': 0}, status=404)

@login_required
def bursor_get_student_class(request):
    student_id = request.GET.get('student_id')
    try:
        student = Student.objects.get(id=student_id)
        return JsonResponse({'current_class': student.current_class.name})
    except Student.DoesNotExist:
        return JsonResponse({'current_class': ''}, status=404)

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from .models import BursorAnswer, InvoiceComments
from .forms import BursorAnswerForm
from apps.corecode.models import AcademicSession

class BursorCommentsListView(LoginRequiredMixin, ListView):
    model = InvoiceComments
    template_name = 'bursor/bursor_comments_list.html'
    context_object_name = 'invoice_comments'

    def get_queryset(self):
        current_session = AcademicSession.objects.filter(current=True).first()
        session_id = self.request.GET.get('session_id')
        if session_id:
            current_session = get_object_or_404(AcademicSession, id=session_id)

        invoice_comments = InvoiceComments.objects.filter(session=current_session).select_related('student', 'parent')

        for comment in invoice_comments:
            bursor_answer = BursorAnswer.objects.filter(comment=comment).first()
            comment.bursor_answer = bursor_answer

        return invoice_comments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = AcademicSession.objects.all()
        context['current_session'] = self.request.GET.get('session_id', AcademicSession.objects.filter(current=True).first().id)
        context['bursor_answer_form'] = BursorAnswerForm()
        return context

    def post(self, request, *args, **kwargs):
        form = BursorAnswerForm(request.POST, request.FILES)
        if form.is_valid():
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(InvoiceComments, id=comment_id)

            try:
                with transaction.atomic():
                    bursor_answer, created = BursorAnswer.objects.get_or_create(
                        student=comment.student,
                        invoice=comment.invoice,
                        session=comment.session,
                        installment=comment.installment,
                        parent=comment.parent,
                        comment=comment,
                        defaults={
                            'answer': form.cleaned_data['answer'],
                            'audio_answer': request.FILES.get('audio_answer')
                        }
                    )

                    if not created:
                        bursor_answer.answer = form.cleaned_data['answer']
                        if 'audio_answer' in request.FILES:
                            bursor_answer.audio_answer = request.FILES['audio_answer']
                        bursor_answer.save()

                    messages.success(request, "Bursor answer saved successfully.")
            except Exception as e:
                messages.error(request, f"There was an error saving the answer: {str(e)}")
        else:
            messages.error(request, "Invalid form submission.")
            print("Form errors:", form.errors)

        return redirect(reverse('bursor_comments') + f'?session_id={comment.session.id}')

def mark_comment_as_satisfied(request, comment_id):
    comment = get_object_or_404(InvoiceComments, id=comment_id)
    comment.satisfied = True
    comment.save()
    messages.success(request, "Comment marked as satisfied.")
    return redirect(reverse('bursor_comments') + f'?session_id={comment.session.id}')

def save_bursor_answer(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(InvoiceComments, id=comment_id)

        form = BursorAnswerForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    bursor_answer, created = BursorAnswer.objects.get_or_create(
                        comment=comment,
                        defaults={
                            'student': comment.student,
                            'invoice': comment.invoice,
                            'session': comment.session,
                            'installment': comment.installment,
                            'parent': comment.parent,
                            'answer': form.cleaned_data['answer'],
                            'audio_answer': request.FILES.get('audio_answer')
                        }
                    )

                    # Update the answer if it already exists
                    if not created:
                        bursor_answer.answer = form.cleaned_data['answer']
                        if 'audio_answer' in request.FILES:
                            bursor_answer.audio_answer = request.FILES['audio_answer']
                        bursor_answer.save()

                    messages.success(request, "Bursor answer saved successfully.")
            except Exception as e:
                messages.error(request, f"There was an error saving the Bursor answer: {str(e)}")
        else:
            messages.error(request, "Invalid form submission.")
            print("Form errors:", form.errors)

        return redirect(reverse('bursor_comments') + f'?session_id={comment.session.id}')

    return redirect('bursor_comments')
