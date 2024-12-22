
import csv
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
import csv
from .forms import StudentForm 
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Student, StudentBulkUpload
from apps.corecode.models import StudentClass
from apps.finance.models import Invoice
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from .models import Student
from apps.staffs.models import Staff
from apps.result.models import Result, StudentInfos



class StudentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = "students/student_list.html"
    permission_required = 'students.view_student_list'
    permission_denied_message = 'Access Denied'
    context_object_name = "students"

    def get_queryset(self):
        # Show only non-completed students
        return Student.objects.filter(completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all classes from the database
        context['student_classes'] = StudentClass.objects.all()
        # Optionally, pre-calculate totals for male/female/overall if you want initial KPIs
        context['total_male'] = Student.objects.filter(gender='male', completed=False).count()
        context['total_female'] = Student.objects.filter(gender='female', completed=False).count()
        context['overall_total'] = Student.objects.filter(completed=False).count()
        return context


class ActiveStudentListView(StudentListView):
    def get_queryset(self):
        return Student.objects.filter(current_status="active", completed=False)

class InactiveStudentsView(StudentListView):
    """
    A view to list all inactive students.
    """
    def get_queryset(self):
        return Student.objects.filter(current_status="inactive", completed=False)


class SelectAlluiClassView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'students.change_student'
    permission_denied_message = 'Access Denied'

    def get(self, request, *args, **kwargs):
        classes = StudentClass.objects.all().order_by('name')
        return render(request, 'students/select_allui_class.html', {'classes': classes})

    def post(self, request, *args, **kwargs):
        selected_class = request.POST.get('selected_class')
        if selected_class:
            Student.objects.filter(current_class__name=selected_class).update(current_status="inactive", completed=True)
            messages.success(request, f"All students in class {selected_class.upper()} have been marked as completed.")
        else:
            messages.error(request, "No class selected.")
        return redirect('completed-students')

from django.db.models import Q

class CompletedStudentsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = "students/completed_student_list.html"
    permission_required = 'students.view_student_list'
    permission_denied_message = 'Access Denied'
    context_object_name = "students"

    def get_queryset(self):
        # Retrieve students matching the conditions
        return Student.objects.filter(
            Q(current_status="inactive", completed=True) |
            Q(current_status="active", completed=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        return context

class CompletedStudentDetailView(DetailView):
    model = Student
    template_name = "students/completed_student_detail.html"
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

class StudentDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Student
    template_name = "students/student_detail.html"
    permission_required = 'students.view_student_detail'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payments"] = Invoice.objects.filter(student=self.object)
        return context


class StudentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentForm  # Use the custom form
    success_message = "New student successfully added."
    permission_required = 'students.add_student'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student_classes"] = StudentClass.objects.all()
        return context

    def form_valid(self, form):
        self.log_debug_info("Form is valid", form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        self.log_debug_info("Form is invalid", form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('student-list')

    def log_debug_info(self, message, data):
        """ Optional: Use Django's logging framework in production """
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: {message}")
        logger.debug(f"DEBUG: Data = {data}")

class StudentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentForm  # Use the custom form
    success_message = "Record successfully updated."
    permission_required = 'students.change_student'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student_classes"] = StudentClass.objects.all()
        return context

    def form_valid(self, form):
        self.log_debug_info("Form is valid", form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        self.log_debug_info("Form is invalid", form.errors)
        return super().form_invalid(form)

class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    success_url = reverse_lazy("student-list")
    permission_required = 'students.delete_student'

class StudentBulkUploadView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentBulkUpload
    template_name = "students/students_upload.html"
    fields = ["csv_file"]
    success_url = reverse_lazy("student-list")
    success_message = "Successfully uploaded students"
    permission_required = 'students.add_student'  # Adjust as needed


class DownloadCSVViewdownloadcsv(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "registration_number",
                "surname",
                "firstname",
                "middle_name",
                "gender",
                "parent_number",
                "address",
                "current_class",
            ]
        )

        return response
