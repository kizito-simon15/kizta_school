import base64
import logging
from typing import Any, Dict, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from apps.corecode.models import (
    AcademicSession, AcademicTerm, ExamType, Installment, SiteConfig,
    StudentClass, Subject
)
from apps.finance.models import Invoice
from apps.result.models import Result
from apps.staffs.models import Staff
from apps.students.models import Student
from library.models import Book, IssuedBook, Stationery
from parents.models import ParentComments, StudentComments, InvoiceComments
from school_properties.models import Property
from .forms import (
    AcademicSessionForm, AcademicTermForm, ExamTypeForm, InstallmentForm, CurrentSessionForm,
    SiteConfigForm, StudentClassForm, SubjectForm, SignatureForm
)
from .models import Signature
from analytics.utils import (
    draw_class_performance_trends,
    draw_subject_trends_for_class,
    draw_student_trends_in_classes,
    cluster_subjects_by_performance,
    draw_expenditure_heatmap_and_waterfall,
    draw_salary_distribution_charts,
    generate_profit_pie_chart,
    draw_linear_regression_graph,
    draw_expenses_analysis,
    draw_salary_variation_line_chart
)

logger = logging.getLogger(__name__)


class IndexView(LoginRequiredMixin, TemplateView):
    """
    The index view acts as a dashboard, providing an overview of key performance indicators (KPIs),
    basic academic statistics, and various analytics charts for both academic and financial metrics.
    """
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Gather all the necessary data for the dashboard and inject it into the template context.

        This includes:
        - Basic KPIs (e.g., total students, staff, invoices, results)
        - Current session, term, exam, and installment data
        - Passing/failing statistics
        - Unresolved parent and student comments
        - Various analytics charts (class performance, subject trends, student trends, profit distribution, etc.)
        """
        context = super().get_context_data(**kwargs)

        # Fetch current academic context
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam_type = ExamType.objects.filter(current=True).first()
        current_installment = Installment.objects.filter(current=True).first()

        # Basic KPIs
        total_students = Student.objects.count()
        total_staffs = Staff.objects.count()
        active_students = Student.objects.filter(current_status="active", completed=False).count()
        active_staff = Staff.objects.filter(current_status="active").count()

        total_invoices = (
            Invoice.objects.filter(session=current_session, installment=current_installment).count()
            if current_session and current_installment else 0
        )

        total_results = (
            Result.objects.filter(session=current_session, term=current_term, exam=current_exam_type).count()
            if current_session and current_term and current_exam_type else 0
        )

        # Prepare KPI list for display
        context["kpi_list"] = [
            {"title": "Total Students", "value": total_students, "detail": active_students, "icon": "👩‍🎓"},
            {"title": "Total Staff", "value": total_staffs, "detail": active_staff, "icon": "👨‍🏫"},
            {"title": "Total Invoices", "value": total_invoices, "icon": "💳"},
            {"title": "Total Results", "value": total_results, "icon": "📊"},
        ]

        # Unresolved comments
        context["parent_comments"] = ParentComments.objects.filter(mark_comment=False)
        context["student_comments"] = StudentComments.objects.filter(mark_student_comment=False)

        # Compute pass/fail stats if session data is available
        pass_count, fail_count = self._compute_pass_fail_counts(current_session, current_term, current_exam_type)
        context["pass_count"] = pass_count
        context["fail_count"] = fail_count
        context["pass_percentage"] = self._compute_pass_percentage(pass_count, fail_count)

        # Analytics and charts
        try:
            self._add_analytics_to_context(context)
        except Exception as e:
            logger.error(f"Error generating analytics data: {e}", exc_info=True)
            context["analytics_error"] = f"Error generating analytics: {e}"

        return context

    def _compute_pass_fail_counts(
        self,
        current_session: Optional[AcademicSession],
        current_term: Optional[AcademicTerm],
        current_exam_type: Optional[ExamType]
    ) -> (int, int):
        """Compute the number of passing and failing results."""
        if current_session and current_term and current_exam_type:
            pass_count = Result.objects.filter(session=current_session, term=current_term, exam=current_exam_type, status="PASS").count()
            fail_count = Result.objects.filter(session=current_session, term=current_term, exam=current_exam_type, status="FAIL").count()
            return pass_count, fail_count
        return 0, 0

    def _compute_pass_percentage(self, pass_count: int, fail_count: int) -> Optional[float]:
        """Compute the pass percentage based on pass and fail counts."""
        total = pass_count + fail_count
        if total > 0:
            return (pass_count * 100.0) / total
        return None

    def _add_analytics_to_context(self, context: Dict[str, Any]) -> None:
        """Add analytics charts and data to the context."""
        # Academic analytics
        class_performance = draw_class_performance_trends()
        subject_performance = draw_subject_trends_for_class()
        student_trends = draw_student_trends_in_classes()
        cluster_chart, cluster_labels, cluster_error = cluster_subjects_by_performance()

        context["class_performance_trends"] = class_performance
        context["subject_performance_trends"] = subject_performance
        context["student_trends_data"] = student_trends

        if cluster_error:
            context["subject_clustering_error"] = cluster_error
        else:
            context["subject_cluster_chart"] = cluster_chart
            context["subject_cluster_labels"] = cluster_labels

        # Financial analytics
        profit_pie_chart, profit_error = generate_profit_pie_chart()
        if profit_error:
            context["profit_pie_chart_error"] = profit_error
            context["profit_pie_chart"] = None
        else:
            context["profit_pie_chart"] = profit_pie_chart

        salary_distribution = draw_salary_distribution_charts()
        occupation_chart, staff_chart, salary_error, salary_by_occupation, salary_by_staff, total_salary = salary_distribution
        context["salary_pie_chart"] = occupation_chart
        if salary_error:
            context["salary_distribution_error"] = salary_error
        context["salary_by_occupation"] = salary_by_occupation
        context["salary_by_staff"] = salary_by_staff
        context["total_salary_distribution"] = total_salary

        expenditure_analysis = draw_expenditure_heatmap_and_waterfall()
        heatmap, waterfall, total_initial_balance, category_expenditures, remaining_balance, trend_description, exp_error = expenditure_analysis
        context["expenditure_heatmap"] = heatmap
        context["expenditure_waterfall"] = waterfall
        context["total_initial_balance"] = total_initial_balance
        context["category_expenditures"] = category_expenditures
        context["remaining_balance"] = remaining_balance
        context["expenditure_trend_description"] = trend_description
        if exp_error:
            context["expenditure_analysis_error"] = exp_error

        regression_analysis = draw_linear_regression_graph()
        regression_graph, balance_data, predicted_profit, predicted_expenses, predicted_balance, regression_comments = regression_analysis
        context["regression_graph"] = regression_graph
        context["balance_data"] = balance_data
        context["predicted_profit"] = predicted_profit
        context["predicted_expenses"] = predicted_expenses
        context["predicted_balance"] = predicted_balance
        context["regression_comments"] = regression_comments

        salary_variation = draw_salary_variation_line_chart()
        salary_variation_chart, salary_variation_data, salary_variation_error = salary_variation
        if salary_variation_error:
            context["salary_variation_error"] = salary_variation_error
        else:
            context["salary_variation_chart"] = salary_variation_chart
            context["salary_variation_data"] = salary_variation_data

        expenses_analysis_data = draw_expenses_analysis()
        (expenses_pie_chart, total_salaries, total_expenditures, overall_total_expenses, expenses_comments) = expenses_analysis_data
        context["expenses_pie_chart"] = expenses_pie_chart
        context["total_salaries"] = total_salaries
        context["total_expenditures"] = total_expenditures
        context["overall_total_expenses"] = overall_total_expenses
        context["expenses_comments"] = expenses_comments




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
    template_name = "corecode/session_form.html"
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
    template_name = "corecode/session_form.html"
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
    template_name = "corecode/term_form.html"
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
    template_name = "corecode/exam_form.html"
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
    """
    View to create a new class
    """
    model = StudentClass
    form_class = StudentClassForm
    template_name = "corecode/mgt_form.html"
    success_url = reverse_lazy("classes")
    success_message = "New class successfully added"
    permission_required = "corecode.add_studentclass"

    def get_context_data(self, **kwargs):
        """
        Add additional context for rendering
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Class"
        context["submit_text"] = "Save Class"
        return context

    def form_valid(self, form):
        """
        Additional form processing before saving
        """
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submission
        """
        messages.error(self.request, "There was an error saving the class. Please check the form and try again.")
        return super().form_invalid(form)

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
    context_object_name = "subjects"

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SubjectForm()  # If needed for inline form usage
        context["search_query"] = self.request.GET.get('search', '')
        return context


class SubjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "corecode/subject_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "New subject successfully added"
    permission_required = "corecode.add_subject"


class SubjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    form_class = SubjectForm  # Use the same styled form
    template_name = "corecode/subject_form.html"
    success_url = reverse_lazy("subjects")
    success_message = "Subject successfully updated."
    permission_required = "corecode.change_subject"


class SubjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Subject
    template_name = "corecode/subject_confirm_delete.html"  # Updated template
    success_url = reverse_lazy("subjects")
    success_message = "The subject {} has been deleted with all its attached content"
    permission_required = "corecode.delete_subject"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message.format(obj.name))
        return super().delete(request, *args, **kwargs)


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
