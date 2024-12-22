from django.urls import path
from .views import (
    analytics_home,
    academic_analysis,
    finance_analysis,
    class_performance_view,
    subject_trends_view,
    student_trends_view,
    salary_distribution_view,
    profit_analysis_view,
    expenditure_analysis_view
)

urlpatterns = [
    path('analytics/', analytics_home, name='analytics-home'),
    path('analytics/academic/', academic_analysis, name='academic_analysis'),
    path('analytics/finance/', finance_analysis, name='finance_analysis'),
    path('performance-trends/', class_performance_view, name='performance_trends'),
    path('subject-trends/', subject_trends_view, name='subject_trends'),
    path('student-trends/', student_trends_view, name='student_trends'),
    path('finance/salary-distribution/', salary_distribution_view, name='salary_distribution'),
    path('expenditure-analysis/', expenditure_analysis_view, name='expenditure_analysis'),
    path('profit-analysis/', profit_analysis_view, name='profit_analysis'),
]

