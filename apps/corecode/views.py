from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.result.models import Result
from library.models import Book, IssuedBook, Stationery
from school_properties.models import Property
from apps.finance.models import Invoice, InvoiceItem, Receipt
from .forms import (
    AcademicSessionForm,
    AcademicTermForm,
    ExamTypeForm,
    InstallmentForm,
    CurrentSessionForm,
    SiteConfigForm,
    StudentClassForm,
    SubjectForm,
)
from .models import (
    AcademicSession,
    AcademicTerm,
    ExamType,
    SiteConfig,
    StudentClass,
    Subject,
    Installment,
)

from parents.models import ParentComments, StudentComments, InvoiceComments 
from django.shortcuts import render, redirect
from .forms import SignatureForm
from .models import Signature
import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Counting total number of students
        total_students = Student.objects.count()

        # Counting total number of staff
        total_staffs = Staff.objects.count()

        # Retrieve current session, term, exam, and installment
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = ExamType.objects.filter(current=True).first()
        current_installment = Installment.objects.filter(current=True).first()

        # Counting total number of invoices for current session and installment
        if current_session and current_installment:
            total_invoices_current = Invoice.objects.filter(
                session=current_session,
                installment=current_installment
            ).count()
        else:
            total_invoices_current = 0

        # Counting total number of results for current session, term, and exam
        if current_session and current_term and current_exam:
            total_results_current = Result.objects.filter(
                session=current_session,
                term=current_term,
                exam=current_exam
            ).count()
        else:
            total_results_current = 0

        # Counting total number of active students who have not completed
        active_students_not_completed = Student.objects.filter(
            current_status="active",
            completed=False
        ).count()

        # Counting total number of active staff who have not completed
        active_staff_not_completed = Staff.objects.filter(
            current_status="active",
        ).count()

        # Counting total number of books
        total_books = Book.objects.count()

        # Counting total number of properties
        total_properties = Property.objects.count()

        # Retrieve comments with specific flags set to False
        student_comments = StudentComments.objects.filter(mark_student_comment=False)
        parent_comments = ParentComments.objects.filter(mark_comment=False)
        invoice_comments = InvoiceComments.objects.filter(satisfied=False)

        # Adding counts and student names to context
        context['student_comments'] = student_comments
        context['parent_comments'] = parent_comments
        context['invoice_comments'] = invoice_comments

        # Adding other counts to context
        context['total_students'] = total_students
        context['total_staffs'] = total_staffs
        context['total_invoices_current'] = total_invoices_current
        context['total_results_current'] = total_results_current
        context['total_books'] = total_books
        context['total_properties'] = total_properties
        context['active_students_not_completed'] = active_students_not_completed
        context['active_staff_not_completed'] = active_staff_not_completed

        return context

class SiteConfigView(LoginRequiredMixin, View):
    """Site Config View"""

    form_class = SiteConfigForm
    template_name = "corecode/siteconfig.html"

    def get(self, request, *args, **kwargs):
        formset = self.form_class(queryset=SiteConfig.objects.all())
        context = {"formset": formset}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        formset = self.form_class(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Configurations successfully updated")
        context = {"formset": formset, "title": "Configuration"}
        return render(request, self.template_name, context)



class SessionListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicSession
    template_name = "corecode/session_list.html"
    permission_required = "corecode.view_academicsession"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicSessionForm()
        return context

class SessionCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("sessions")
    success_message = "New session successfully added"
    permission_required = "corecode.add_academicsession"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add new session"
        return context



class SessionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicSession
    form_class = AcademicSessionForm
    success_url = reverse_lazy("sessions")
    success_message = "Session successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_academicsession"

    def form_valid(self, form):
        obj = self.object
        if not obj.current:
            terms = (
                AcademicSession.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a session to current.")
                return redirect("session-list")
        return super().form_valid(form)


class SessionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AcademicSession
    success_url = reverse_lazy("sessions")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The session {} has been deleted with all its attached content"
    permission_required = "corecode.delete_academicsession"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete session as it is set to current")
            return redirect("sessions")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SessionDeleteView, self).delete(request, *args, **kwargs)


class TermListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = AcademicTerm
    template_name = "corecode/term_list.html"
    permission_required = "corecode.view_academicterm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AcademicTermForm()
        return context


class TermCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("terms")
    success_message = "New term successfully added"
    permission_required = "corecode.add_academicterm"


class TermUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = AcademicTerm
    form_class = AcademicTermForm
    success_url = reverse_lazy("terms")
    success_message = "Term successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_academicterm"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            terms = (
                AcademicTerm.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not terms:
                messages.warning(self.request, "You must set a term to current.")
                return redirect("term")
        return super().form_valid(form)


class TermDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AcademicTerm
    success_url = reverse_lazy("terms")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The term {} has been deleted with all its attached content"
    permission_required = "corecode.delete_academicterm"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete term as it is set to current")
            return redirect("terms")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(TermDeleteView, self).delete(request, *args, **kwargs)


class ExamListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = ExamType
    template_name = "corecode/exam_list.html"
    permission_required = "corecode.view_examtype"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ExamTypeForm()
        return context


class ExamCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExamType
    form_class = ExamTypeForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("exams")
    success_message = "New exam type successfully added"
    permission_required = "corecode.add_examtype"


class ExamUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ExamType
    form_class = ExamTypeForm
    success_url = reverse_lazy("exams")
    success_message = "Exam type successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_examtype"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            exams = (
                ExamType.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not exams:
                messages.warning(self.request, "You must set an exam type to current.")
                return redirect("exam")
        return super().form_valid(form)


class ExamDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = ExamType
    success_url = reverse_lazy("exams")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The exam type {} has been deleted with all its attached content"
    permission_required = "corecode.delete_examtype"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete exam type as it is set to current")
            return redirect("exams")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ExamDeleteView, self).delete(request, *args, **kwargs)

class InstallListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = Installment
    template_name = "corecode/install_list.html"
    permission_required = "corecode.view_installment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InstallmentForm()
        return context


class InstallCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Installment
    form_class = InstallmentForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("installs")
    success_message = "New installment successfully added"
    permission_required = "corecode.add_installment"


class InstallUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Installment
    form_class = InstallmentForm
    success_url = reverse_lazy("installs")
    success_message = "Installment successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_installment"

    def form_valid(self, form):
        obj = self.object
        if obj.current == False:
            installs = (
                Installment.objects.filter(current=True)
                .exclude(name=obj.name)
                .exists()
            )
            if not installs:
                messages.warning(self.request, "You must set an installment to current.")
                return redirect("installs")
        return super().form_valid(form)


class InstallDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Installment
    success_url = reverse_lazy("installs")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The installment {} has been deleted with all its attached content"
    permission_required = "corecode.delete_installment"


    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.current == True:
            messages.warning(request, "Cannot delete installment as it is set to current")
            return redirect("installs")
        messages.success(self.request, self.success_message.format(obj.name))
        return super(InstallDeleteView, self).delete(request, *args, **kwargs)

class ClassListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = StudentClass
    template_name = "corecode/class_list.html"
    permission_required = "corecode.view_studentclass"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = StudentClassForm()
        return context


class ClassCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = StudentClass
    form_class = StudentClassForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("classes")
    success_message = "New class successfully added"
    permission_required = "corecode.add_studentclass"


class ClassUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StudentClass
    fields = ["name"]
    success_url = reverse_lazy("classes")
    success_message = "class successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_studentclass"


class ClassDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = StudentClass
    success_url = reverse_lazy("classes")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The class {} has been deleted with all its attached content"
    permission_required = "corecode.delete_studentclass"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        print(obj.name)
        messages.success(self.request, self.success_message.format(obj.name))
        return super(ClassDeleteView, self).delete(request, *args, **kwargs)


class SubjectListView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, ListView):
    model = Subject
    template_name = "corecode/subject_list.html"
    permission_required = "corecode.view_subject"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SubjectForm()
        return context


class SubjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "New subject successfully added"
    permission_required = "corecode.add_subject"


class SubjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    fields = ["name"]
    success_url = reverse_lazy("subjects")
    success_message = "Subject successfully updated."
    template_name = "corecode/mgt_form.html"
    permission_required = "corecode.change_subject"


class SubjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy("subjects")
    template_name = "corecode/core_confirm_delete.html"
    success_message = "The subject {} has been deleted with all its attached content"
    permission_required = "corecode.delete_subject"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super(SubjectDeleteView, self).delete(request, *args, **kwargs)


class CurrentSessionAndTermAndExamTypeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Current SEssion and Term and Exam Type"""

    form_class = CurrentSessionForm
    template_name = "corecode/current_session.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class(
            initial={
                "current_session": AcademicSession.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
                "current_exam": ExamType.objects.get(current=True),
            }
        )
        return render(request, self.template_name, {"form": form})
    def post(self, request, *args, **kwargs):
        form = self.form_class(
            request.POST,
            initial={
                "current_session": AcademicSession.objects.get(current=True),
                "current_term": AcademicTerm.objects.get(current=True),
                "current_exam": ExamType.objects.get(current=True),
            }
        )
        if form.is_valid():
            session = form.cleaned_data["current_session"]
            term = form.cleaned_data["current_term"]
            exam = form.cleaned_data["current_exam"]
            AcademicSession.objects.filter(name=session).update(current=True)
            AcademicSession.objects.exclude(name=session).update(current=False)
            AcademicTerm.objects.filter(name=term).update(current=True)
            ExamType.objects.filter(name=exam).update(current=True)

        return render(request, self.template_name, {"form": form})

def create_signature(request):
    if request.method == 'POST':
        form = SignatureForm(request.POST)
        if form.is_valid():
            signature = form.save(commit=False)

            # Get the signature image data from the request
            signature_data = request.POST.get('signature_data')
            format, imgstr = signature_data.split(';base64,')
            ext = format.split('/')[-1]
            signature_image = ContentFile(base64.b64decode(imgstr), name=f'{signature.name}_signature.{ext}')
            signature.signature_image = signature_image

            signature.save()
            return redirect('signature_list')
    else:
        form = SignatureForm()
    
    return render(request, 'corecode/create_signature.html', {'form': form})

def signature_list(request):
    signatures = Signature.objects.all()
    return render(request, 'corecode/signature_list.html', {'signatures': signatures})

def delete_signature(request, pk):
    signature = get_object_or_404(Signature, pk=pk)
    if request.method == 'POST':
        signature.delete()
        messages.success(request, 'Signature deleted successfully.')
        return redirect('signature_list')
    
    return render(request, 'corecode/delete_signature.html', {'signature': signature})
