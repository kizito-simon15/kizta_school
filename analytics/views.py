import logging
from datetime import datetime
from typing import Any, Dict, Optional, List

from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .utils import (
    draw_class_performance_trends,
    draw_subject_trends_for_class,
    draw_student_trends_in_classes,
    draw_salary_distribution_charts,
    draw_salary_variation_line_chart,
    draw_expenditure_heatmap_and_waterfall,
    draw_expenses_analysis,
    draw_linear_regression_graph,
    generate_profit_pie_chart,
    cluster_subjects_by_performance
)

from apps.finance.models import Receipt, StudentUniform
from apps.corecode.models import AcademicSession
from expenditures.models import ExpenditureInvoice

logger = logging.getLogger(__name__)


def analytics_home(request: HttpRequest) -> HttpResponse:
    """
    Landing page for the analytics section, providing quick links to academic and finance analytics pages.
    """
    logger.debug("Rendering analytics home page.")
    return render(request, 'analytics/home.html')


def academic_analysis(request: HttpRequest) -> HttpResponse:
    """
    Academic analytics main view, providing links or brief overviews of academic metrics such as
    class performance or subject trends.
    """
    logger.debug("Rendering academic_analysis view.")
    return render(request, 'analytics/academic_analysis.html')


def finance_analysis(request: HttpRequest) -> HttpResponse:
    """
    Finance analytics main view, offering summaries and links to detailed views of profits, expenditures,
    salary distributions, and other financial KPIs.
    """
    logger.debug("Rendering finance_analysis view.")
    return render(request, 'analytics/finance_analysis.html')


def class_performance_view(request: HttpRequest) -> HttpResponse:
    """
    Renders performance trends for all classes using the draw_class_performance_trends utility.
    If no data is available, a message is shown.
    """
    logger.debug("Generating class performance trends.")
    graphs = draw_class_performance_trends()
    if not graphs:
        message = "No performance data available for any class."
    else:
        no_data = all(v['graph'] is None for v in graphs.values())
        message = "No data for classes." if no_data else None

    return render(request, 'analytics/performance_trends.html', {
        'graphs': graphs,
        'message': message,
    })


def subject_trends_view(request: HttpRequest) -> HttpResponse:
    """
    Displays subject trends for each class using draw_subject_trends_for_class.
    Shows a message if no data is available for some or all classes.
    """
    logger.debug("Generating subject trends for each class.")
    subject_trends = draw_subject_trends_for_class()

    no_data_classes = [cls for cls, subjects in subject_trends.items() if not subjects]
    if not subject_trends:
        message = "No subject trend data available."
    elif no_data_classes:
        message = f"Some classes have no subject trend data: {', '.join(no_data_classes)}"
    else:
        message = None

    return render(request, 'analytics/subject_trends.html', {
        'subject_trends': subject_trends,
        'no_data_classes': no_data_classes,
        'message': message,
    })


def student_trends_view(request: HttpRequest) -> HttpResponse:
    """
    Displays student performance trends within their classes, using draw_student_trends_in_classes.
    Shows a message if no data is available.
    """
    logger.debug("Generating student trends.")
    student_trends = draw_student_trends_in_classes()
    message = "No student trend data available." if not student_trends else None

    return render(request, 'analytics/student_trends.html', {
        'student_trends': student_trends,
        'message': message
    })


def subject_clustering_view(request: HttpRequest) -> HttpResponse:
    """
    Displays clusters of subjects by performance using cluster_subjects_by_performance.
    If clustering fails, an error message is shown.
    """
    logger.debug("Clustering subjects by performance.")
    cluster_chart, cluster_labels, error = cluster_subjects_by_performance()

    message = error if error else None

    return render(request, 'analytics/subject_clusters.html', {
        'cluster_chart': cluster_chart,
        'cluster_labels': cluster_labels,
        'message': message
    })


def salary_distribution_view(request: HttpRequest) -> HttpResponse:
    """
    Shows salary distribution by occupation and staff, as well as salary variation over time.
    Integrates data from draw_salary_distribution_charts and draw_salary_variation_line_chart.
    """
    logger.debug("Generating salary distribution and variation charts.")
    (occupation_chart, staff_chart, error_message,
     salary_by_occupation, salary_by_staff, total_salary) = draw_salary_distribution_charts()

    salary_variation_chart, salary_variation_data, salary_variation_error = draw_salary_variation_line_chart()

    combined_error = error_message or salary_variation_error
    if combined_error:
        logger.warning(f"Salary analytics warning: {combined_error}")

    context = {
        'occupation_chart': occupation_chart,
        'staff_chart': staff_chart,
        'error_message': combined_error,
        'salary_by_occupation': salary_by_occupation,
        'salary_by_staff': salary_by_staff,
        'total_salary': total_salary,
        'salary_variation_chart': salary_variation_chart,
        'salary_variation_data': salary_variation_data,
    }
    return render(request, 'analytics/salary_distribution.html', context)


def expenditure_analysis_view(request: HttpRequest) -> HttpResponse:
    """
    Displays expenditure analysis including heatmap and waterfall charts, along with insights.
    Utilizes draw_expenditure_heatmap_and_waterfall utility.
    """
    logger.debug("Generating expenditure analysis charts.")
    (heatmap, waterfall, total_initial_balance, category_expenditures,
     remaining_balance, trend_description, error_message) = draw_expenditure_heatmap_and_waterfall()

    current_year = datetime.now().year

    if error_message:
        logger.warning(f"Expenditure analysis warning: {error_message}")

    context = {
        'heatmap': heatmap,
        'waterfall': waterfall,
        'total_initial_balance': total_initial_balance,
        'category_expenditures': category_expenditures,
        'remaining_balance': remaining_balance,
        'trend_description': trend_description,
        'error_message': error_message,
        'current_year': current_year,
    }
    return render(request, 'analytics/expenditure_analysis.html', context)


def profit_analysis_view(request: HttpRequest) -> HttpResponse:
    """
    Analyzes profit distribution, expenses, and uses regression for future balance predictions.
    Combines data from multiple utilities to provide a comprehensive financial overview.
    """
    logger.debug("Generating profit analysis.")
    current_session = AcademicSession.objects.filter(current=True).first()
    if not current_session:
        logger.error("No active academic session found for profit analysis.")
        return render(request, 'analytics/profit_analysis.html', {
            'error_message': "No active session found."
        })

    profit_pie_chart, profit_chart_error = generate_profit_pie_chart()
    if profit_chart_error:
        logger.warning(f"Profit pie chart error: {profit_chart_error}")
        return render(request, 'analytics/profit_analysis.html', {'error_message': profit_chart_error})

    total_receipts = (
        Receipt.objects.filter(invoice__session=current_session)
        .aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    )
    total_uniforms = (
        StudentUniform.objects.filter(session=current_session)
        .aggregate(Sum('amount'))['amount__sum'] or 0
    )
    overall_total_income = total_receipts + total_uniforms

    if total_receipts > total_uniforms:
        profit_comments = (
            "Receipts form the bulk of income. Consider strengthening uniform sales or other revenue streams for diversification."
        )
    elif total_uniforms > total_receipts:
        profit_comments = (
            "Uniform sales are the main revenue source. Explore improving receipt collections for better balance."
        )
    else:
        profit_comments = "Receipts and uniform sales are balanced. Maintain this equilibrium."

    (expenses_pie_chart, total_salaries, total_expenditures, overall_total_expenses,
     expenses_comments) = draw_expenses_analysis()

    (regression_graph, balance_data, predicted_profit, predicted_expenses,
     predicted_balance, regression_comments) = draw_linear_regression_graph()

    remaining_balance = overall_total_income - overall_total_expenses
    if remaining_balance > 0:
        balance_comments = (
            f"The school has a surplus of TZS {remaining_balance:,.2f}, indicating positive financial health. "
            "Consider investing surplus in future growth or saving for emergencies."
        )
    elif remaining_balance < 0:
        balance_comments = (
            f"The school is running a deficit of TZS {abs(remaining_balance):,.2f}. "
            "Immediate cost reduction or revenue enhancement measures should be considered."
        )
    else:
        balance_comments = (
            f"The school broke even, with a balance of TZS {remaining_balance:,.2f}. "
            "Maintain stability but aim for future surplus."
        )

    context = {
        'current_session': current_session.name,
        'profit_pie_chart': profit_pie_chart,
        'total_receipts': total_receipts,
        'total_uniforms': total_uniforms,
        'overall_total_income': overall_total_income,
        'profit_comments': profit_comments,
        'expenses_pie_chart': expenses_pie_chart,
        'total_salaries': total_salaries,
        'total_expenditures': total_expenditures,
        'overall_total_expenses': overall_total_expenses,
        'expenses_comments': expenses_comments,
        'remaining_balance': remaining_balance,
        'balance_comments': balance_comments,
        'regression_graph': regression_graph,
        'balance_data': balance_data,
        'predicted_profit': predicted_profit,
        'predicted_expenses': predicted_expenses,
        'predicted_balance': predicted_balance,
        'regression_comments': regression_comments,
    }

    return render(request, 'analytics/profit_analysis.html', context)


def comprehensive_analytics_view(request: HttpRequest) -> HttpResponse:
    """
    Provides a comprehensive dashboard overview of both academic and financial analytics.
    Logs errors and continues loading whatever data is available.
    """
    logger.debug("Generating a comprehensive analytics overview.")
    context: Dict[str, Any] = {}
    try:
        class_graphs = draw_class_performance_trends()
        context['class_graphs'] = class_graphs
    except Exception as e:
        logger.error(f"Error fetching class performance trends: {e}")
        context['class_graphs_error'] = "Unable to load class performance trends."

    try:
        profit_pie_chart, profit_chart_error = generate_profit_pie_chart()
        if profit_chart_error:
            context['profit_chart_error'] = profit_chart_error
        else:
            context['profit_pie_chart'] = profit_pie_chart
    except Exception as e:
        logger.error(f"Error generating profit pie chart: {e}")
        context['profit_chart_error'] = "Unable to load profit distribution chart."

    return render(request, 'analytics/comprehensive_dashboard.html', context)

