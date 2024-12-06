from django.shortcuts import render

def analytics_home(request):
    return render(request, 'analytics/home.html')

def academic_analysis(request):
    return render(request, 'analytics/academic_analysis.html')

def finance_analysis(request):
    return render(request, 'analytics/finance_analysis.html')

from django.shortcuts import render
from .utils import draw_class_performance_trends

def class_performance_view(request):
    """
    View to render performance trends of all classes.
    """
    graphs = draw_class_performance_trends()
    return render(request, 'analytics/performance_trends.html', {'graphs': graphs})

from django.shortcuts import render
from .utils import draw_subject_trends_for_class

def subject_trends_view(request):
    """
    View to display subject trends for each class.
    """
    subject_trends = draw_subject_trends_for_class()

    # Identify classes without data
    no_data_classes = [class_name for class_name, subjects in subject_trends.items() if not subjects]

    return render(request, 'analytics/subject_trends.html', {
        'subject_trends': subject_trends,
        'no_data_classes': no_data_classes,
    })

from django.shortcuts import render
from .utils import draw_student_trends_in_classes

def student_trends_view(request):
    """
    View to display student performance trends in their respective classes.
    """
    student_trends = draw_student_trends_in_classes()
    return render(request, 'analytics/student_trends.html', {'student_trends': student_trends})

from django.shortcuts import render
from .utils import draw_class_regression_trends

def class_regression_trends_view(request):
    regression_trends = draw_class_regression_trends()
    return render(request, 'analytics/class_regression_trends.html', {'regression_trends': regression_trends})

from .utils import draw_salary_distribution_charts, draw_salary_variation_line_chart

def salary_distribution_view(request):
    occupation_chart, staff_chart, error_message, salary_by_occupation, salary_by_staff, total_salary = draw_salary_distribution_charts()
    salary_variation_chart, salary_variation_data = draw_salary_variation_line_chart()
    context = {
        'occupation_chart': occupation_chart,
        'staff_chart': staff_chart,
        'error_message': error_message,
        'salary_by_occupation': salary_by_occupation,
        'salary_by_staff': salary_by_staff,
        'total_salary': total_salary,
        'salary_variation_chart': salary_variation_chart,
        'salary_variation_data': salary_variation_data,
    }
    return render(request, 'analytics/salary_distribution.html', context)

from datetime import datetime
from .utils import draw_expenditure_heatmap_and_waterfall

from datetime import datetime

def expenditure_analysis_view(request):
    (
        heatmap, 
        waterfall, 
        total_initial_balance, 
        category_expenditures, 
        remaining_balance, 
        trend_description, 
        error_message
    ) = draw_expenditure_heatmap_and_waterfall()

    current_year = datetime.now().year

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

from django.shortcuts import render
from django.db.models import Sum
from apps.finance.models import Receipt, StudentUniform, SalaryInvoice
from apps.corecode.models import AcademicSession
from expenditures.models import ExpenditureInvoice
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from .utils import draw_expenses_analysis, draw_linear_regression_graph

def profit_analysis_view(request):
    current_session = AcademicSession.objects.get(current=True)

    # Total income from receipts
    total_receipts = (
        Receipt.objects.filter(invoice__session=current_session)
        .aggregate(Sum('amount_paid'))['amount_paid__sum']
        or 0
    )

    # Total income from student uniforms
    total_uniforms = (
        StudentUniform.objects.filter(session=current_session)
        .aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    # Overall total income
    overall_total_income = total_receipts + total_uniforms

    # Profit pie chart data
    income_data = {
        'Receipts': total_receipts,
        'Uniforms': total_uniforms,
    }
    income_percentages = {
        k: (v / overall_total_income * 100 if overall_total_income > 0 else 0)
        for k, v in income_data.items()
    }

    # Generate profit pie chart
    income_labels = list(income_data.keys())
    income_sizes = list(income_percentages.values())
    income_colors = ['#4CAF50', '#FFC107']
    plt.figure(figsize=(5, 5))
    plt.pie(
        income_sizes,
        labels=income_labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=income_colors,
    )
    plt.title("Profit Distribution by Source", fontsize=14, fontweight="bold")
    plt.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    profit_pie_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Descriptive profit comments
    if total_receipts > total_uniforms:
        profit_comments = (
            "Receipts contribute the highest to the school's income. Diversify sources by increasing uniform sales."
        )
    elif total_uniforms > total_receipts:
        profit_comments = (
            "Uniform sales dominate the school's income. Focus on improving receipt collection for balance."
        )
    else:
        profit_comments = (
            "Balanced income sources from receipts and uniforms. Maintain consistency for stability."
        )

    # Expenses analysis
    (
        expenses_pie_chart,
        total_salaries,
        total_expenditures,
        overall_total_expenses,
        expenses_comments,
    ) = draw_expenses_analysis()

    # Linear regression graph and predictions
    (
        regression_graph,
        balance_data,
        predicted_profit,
        predicted_expenses,
        predicted_balance,
        regression_comments,
    ) = draw_linear_regression_graph()

    # Balance calculation
    remaining_balance = overall_total_income - overall_total_expenses
    if remaining_balance > 0:
        balance_comments = (
            f"The school has a surplus of TZS {remaining_balance:,.2f}. This indicates good financial health. "
            "Consider investing the surplus in future projects, staff development, or infrastructure upgrades."
        )
    elif remaining_balance < 0:
        balance_comments = (
            f"The school has a deficit of TZS {abs(remaining_balance):,.2f}. Immediate attention is required to manage expenses "
            "and explore ways to increase income. Evaluate unnecessary expenditures and focus on revenue-generating activities."
        )
    else:
        balance_comments = (
            f"The school broke even with a remaining balance of TZS {remaining_balance:,.2f}. While this shows careful spending, "
            "ensure there is room for savings or unforeseen expenses in the future."
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
