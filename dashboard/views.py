from django.views.generic import TemplateView
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.finance.models import Invoice
from apps.result.models import Result
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, Installment
from library.models import Book
from school_properties.models import Property
from parents.models import ParentComments, StudentComments, InvoiceComments

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve comments with False flags
        student_comments = StudentComments.objects.filter(mark_student_comment=False)
        parent_comments = ParentComments.objects.filter(mark_comment=False)
        invoice_comments = InvoiceComments.objects.filter(satisfied=False)

        context['student_comments'] = student_comments
        context['parent_comments'] = parent_comments
        context['invoice_comments'] = invoice_comments

        # Adding other counts to context
        context.update({
            'total_students': Student.objects.count(),
            'total_staffs': Staff.objects.count(),
            'total_invoices_current': Invoice.objects.filter(session=AcademicSession.objects.filter(current=True).first(), installment=Installment.objects.filter(current=True).first()).count() if AcademicSession.objects.filter(current=True).first() and Installment.objects.filter(current=True).first() else 0,
            'total_results_current': Result.objects.filter(session=AcademicSession.objects.filter(current=True).first(), term=AcademicTerm.objects.filter(current=True).first(), exam=ExamType.objects.filter(current=True).first()).count() if AcademicSession.objects.filter(current=True).first() and AcademicTerm.objects.filter(current=True).first() and ExamType.objects.filter(current=True).first() else 0,
            'total_books': Book.objects.count(),
            'total_properties': Property.objects.count(),
            'active_students_not_completed': Student.objects.filter(current_status="active", completed=False).count(),
            'active_staff_not_completed': Staff.objects.filter(current_status="active").count(),
        })

        return context
