from django.urls import path
from .views import analytics_home, academic_analysis, finance_analysis, class_performance_view, subject_trends_view, class_regression_trends_view, salary_distribution_view, profit_analysis_view

from . import views

urlpatterns = [
    path('analytics/', analytics_home, name='analytics-home'),
    # Add paths for 'academic_analysis' and 'finance_analysis' views once they are created
]

urlpatterns += [
    path('analytics/academic/', academic_analysis, name='academic_analysis'),
    path('analytics/finance/', finance_analysis, name='finance_analysis'),
    path('performance-trends/', class_performance_view, name='performance_trends'),
    path('subject-trends/', subject_trends_view, name='subject_trends'),
    path('student-trends/', views.student_trends_view, name='student_trends'),
    path('class-regression-trends/', class_regression_trends_view, name='class_regression_trends'),
    path('finance/salary-distribution/', salary_distribution_view, name='salary_distribution'),
    path('expenditure-analysis/', views.expenditure_analysis_view, name='expenditure_analysis'),
    path('profit-analysis/', profit_analysis_view, name='profit_analysis'),
]
