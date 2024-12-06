
import csv
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import widgets
from django.http import HttpResponse
from django.urls import reverse_lazy
import csv

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
        return Student.objects.filter(current_status="active", completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        return context


class InactiveStudentsView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Student
    template_name = "students/inactive_student_list.html"
    permission_required = 'students.view_student_list'
    permission_denied_message = 'Access Denied'
    context_object_name = "students"

    def get_queryset(self):
        return Student.objects.filter(current_status="inactive", completed=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_classes'] = StudentClass.objects.all()
        context['staff_list'] = Staff.objects.filter(current_status="inactive")
        return context

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

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django import forms
from .models import Student
from apps.corecode.models import StudentClass


class StudentCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    fields = "__all__"  # Include all fields in the form
    success_message = "New student successfully added."
    permission_required = 'students.add_student'
    permission_denied_message = 'Access Denied'

    def get_context_data(self, **kwargs):
        print("DEBUG: Entering get_context_data")
        context = super().get_context_data(**kwargs)
        context["student_classes"] = StudentClass.objects.all()
        print(f"DEBUG: student_classes count = {context['student_classes'].count()}")
        print("DEBUG: Exiting get_context_data")
        return context

    def get_form(self):
        print("DEBUG: Entering get_form")
        form = super(StudentCreateView, self).get_form()
        form.fields["date_of_birth"].widget = forms.DateInput(attrs={"type": "date"})
        form.fields["address"].widget = forms.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = forms.Textarea(attrs={"rows": 2})
        print(f"DEBUG: Form fields = {form.fields.keys()}")
        print("DEBUG: Exiting get_form")
        return form

    def form_valid(self, form):
        print("DEBUG: Entering form_valid")
        print(f"DEBUG: Form data = {form.cleaned_data}")
        response = super().form_valid(form)
        print("DEBUG: Form successfully saved")
        print(f"DEBUG: Saved instance = {self.object}")
        print("DEBUG: Exiting form_valid")
        return response

    def form_invalid(self, form):
        print("DEBUG: Entering form_invalid")
        print(f"DEBUG: Form errors = {form.errors}")
        response = super().form_invalid(form)
        print("DEBUG: Exiting form_invalid")
        return response

    def get_success_url(self):
        print("DEBUG: Entering get_success_url")
        url = reverse_lazy('student-list')
        print(f"DEBUG: Success URL = {url}")
        print("DEBUG: Exiting get_success_url")
        return url

class StudentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    fields = "__all__"
    success_message = "Record successfully updated."
    permission_required = 'students.change_student'
    permission_denied_message = 'Access Denied'


    def get_context_data(self, **kwargs):
        print("DEBUG: Entering get_context_data")
        context = super().get_context_data(**kwargs)
        context["student_classes"] = StudentClass.objects.all()
        print(f"DEBUG: student_classes count = {context['student_classes'].count()}")
        print("DEBUG: Exiting get_context_data")
        return context
    
    def get_form(self):
        form = super(StudentUpdateView, self).get_form()
        form.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        form.fields["date_of_admission"].widget = widgets.DateInput(
            attrs={"type": "date"}
        )
        form.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        form.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        return form


class StudentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
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