from django.views.generic import TemplateView
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.finance.models import Invoice
from apps.result.models import Result
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, Installment
from library.models import Book
from school_properties.models import Property
from parents.models import ParentComments, StudentComments
from analytics.utils import (
    draw_class_performance_trends,
    draw_subject_trends_for_class,
    draw_expenditure_heatmap_and_waterfall,
    draw_salary_distribution_charts,
    draw_salary_variation_line_chart,
    generate_profit_pie_chart,
    draw_linear_regression_graph,
    draw_expenses_analysis,
)


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch current session, term, exam, and installment
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam_type = ExamType.objects.filter(current=True).first()
        current_installment = Installment.objects.filter(current=True).first()

        # Basic KPIs
        total_students = Student.objects.count()
        total_staffs = Staff.objects.count()
        active_students = Student.objects.filter(current_status="active", completed=False).count()
        active_staff = Staff.objects.filter(current_status="active").count()

        # Invoices count
        total_invoices = (
            Invoice.objects.filter(session=current_session, installment=current_installment).count()
            if current_session and current_installment else 0
        )

        # Only count results where test and exam scores are <= 50
        if current_session and current_term and current_exam_type:
            valid_results = Result.objects.filter(
                session=current_session,
                term=current_term,
                exam=current_exam_type,
                test_score__lte=50,
                exam_score__lte=50
            )
            total_results = valid_results.count()
        else:
            total_results = 0

        # Prepare KPI list for template
        context["kpi_list"] = [
            {"title": "Total Students", "value": total_students, "detail": active_students, "icon": "👩‍🎓"},
            {"title": "Total Staff", "value": total_staffs, "detail": active_staff, "icon": "👨‍🏫"},
            {"title": "Total Invoices", "value": total_invoices, "icon": "💳"},
            {"title": "Total Results", "value": total_results, "icon": "📊"},
        ]

        # Unresolved comments
        context.update({
            "parent_comments": ParentComments.objects.filter(mark_comment=False),
            "student_comments": StudentComments.objects.filter(mark_student_comment=False),
        })

        # Analytics and charts
        try:
            # Class performance trends
            class_performance = draw_class_performance_trends()
            # Subject performance trends
            subject_performance = draw_subject_trends_for_class()
            # Profit pie chart
            profit_pie_chart, profit_error = generate_profit_pie_chart()
            # Salary distribution charts
            salary_distribution = draw_salary_distribution_charts()
            # Expenditure heatmap
            expenditure_analysis = draw_expenditure_heatmap_and_waterfall()
            # Regression graph
            regression_analysis = draw_linear_regression_graph()
            # Salary variation line chart
            salary_variation = draw_salary_variation_line_chart()
            # Expenses analysis
            expenses_analysis = draw_expenses_analysis()

            # Update context
            context["class_performance_trends"] = class_performance
            context["subject_performance_trends"] = subject_performance

            # Profit pie chart
            if profit_error:
                context["profit_pie_chart_error"] = profit_error
                context["profit_pie_chart"] = None
            else:
                context["profit_pie_chart"] = profit_pie_chart

            # Salary distribution charts (first element is occupation_chart)
            occupation_chart = salary_distribution[0]
            context["salary_pie_chart"] = occupation_chart

            # Expenditure heatmap (first element is the heatmap)
            heatmap = expenditure_analysis[0]
            context["expenditure_heatmap"] = heatmap

            # Regression graph (first element is the regression graph)
            regression_graph = regression_analysis[0]
            context["regression_graph"] = regression_graph

            # Salary variation line chart
            salary_variation_chart, salary_variation_data, salary_variation_error = salary_variation
            if salary_variation_error:
                context["salary_variation_error"] = salary_variation_error
            else:
                context["salary_variation_chart"] = salary_variation_chart
                context["salary_variation_data"] = salary_variation_data

            # Expenses analysis
            expenses_pie_chart, total_salaries, total_expenditures, overall_total, expenses_comments = expenses_analysis
            context["expenses_pie_chart"] = expenses_pie_chart
            context["total_salaries"] = total_salaries
            context["total_expenditures"] = total_expenditures
            context["overall_total_expenses"] = overall_total
            context["expenses_comments"] = expenses_comments

        except Exception as e:
            context["analytics_error"] = f"Error generating analytics: {e}"

        return context
