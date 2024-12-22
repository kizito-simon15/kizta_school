import base64
import io
import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from django.db.models import Sum, QuerySet
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass, Subject
from apps.finance.models import Invoice, Receipt, SalaryInvoice, StudentUniform
from apps.result.models import Result
from apps.staffs.models import Staff
from apps.students.models import Student
from expenditures.models import Expenditure, ExpenditureInvoice
from parents.models import ParentComments, StudentComments

logger = logging.getLogger(__name__)

############################################
# Helper Functions
############################################

def _figure_to_base64(fig: plt.Figure) -> str:
    """Convert a Matplotlib figure to a base64-encoded string."""
    with BytesIO() as buffer:
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


def use_advanced_model_if_possible(
    x: np.ndarray, 
    y: np.ndarray
) -> Tuple[Union[RandomForestRegressor, LinearRegression], str]:
    """
    Use a RandomForestRegressor if we have sufficient data points; otherwise, fall back to LinearRegression.
    """
    if len(x) > 5:
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(x, y.ravel())
        model_type = "RandomForestRegressor"
    else:
        model = LinearRegression()
        model.fit(x, y)
        model_type = "LinearRegression"
    return model, model_type


def generate_comments_and_advice(
    over_and_over_average: float,
    latest_average: float,
    strongest: List[str],
    medium: List[str],
    weakest: List[str]
) -> str:
    """
    Generate comments and advice based on performance averages and subject strengths/weaknesses.
    Note: over_and_over_average and latest_average are on a 50-point scale.
    """
    advice = []

    # Overall performance commentary based on a scale out of 50
    if over_and_over_average < 10:
        advice.append(
            f"Overall performance is significantly below expectations (Avg: {over_and_over_average:.2f}/50). "
            "A comprehensive support plan is required, including remedial classes and closer monitoring."
        )
    elif over_and_over_average < 25:
        advice.append(
            f"Performance is below average (Avg: {over_and_over_average:.2f}/50). "
            "Implement structured revision plans, additional exercises, and periodic assessments."
        )
    elif over_and_over_average < 40:
        advice.append(
            f"Performance is around average (Avg: {over_and_over_average:.2f}/50). "
            "Consistency is key. Encourage more practice and use formative assessments to identify gaps."
        )
    elif over_and_over_average < 50:
        advice.append(
            f"Good performance (Avg: {over_and_over_average:.2f}/50). "
            "Consider more challenging tasks to push towards excellence and maintain steady growth."
        )
    else:
        # If it ever hits 50, that's a perfect score scenario
        advice.append(
            f"Excellent performance (Avg: {over_and_over_average:.2f}/50). "
            "Continue to provide enrichment activities and encourage peer mentoring to sustain top-level results."
        )

    # Subject-level feedback
    if strongest:
        advice.append(f"Strongest subjects: {', '.join(strongest)}. Leverage these strengths for confidence building.")
    if medium:
        advice.append(f"Moderate subjects: {', '.join(medium)}. Targeted practice can elevate these to strengths.")
    if weakest:
        advice.append(f"Weakest subjects: {', '.join(weakest)}. Allocate additional support or tutoring sessions.")

    return " ".join(advice)


############################################
# Clustering Subjects by Performance
############################################

def cluster_subjects_by_performance() -> Tuple[Optional[str], Dict[str, int], Optional[str]]:
    """
    Use K-Means clustering to group subjects by their average performance (out of 50).
    Returns a base64 chart, a subject-to-cluster map, and an error message if any.
    """
    results = Result.objects.all()
    if not results.exists():
        return None, {}, "No results data for clustering."

    subject_ids = results.values_list('subject', flat=True).distinct()
    subjects = Subject.objects.filter(pk__in=subject_ids)
    subject_averages = []

    for subj in subjects:
        subj_results = results.filter(subject=subj).exclude(average__isnull=True)
        if subj_results.exists():
            # Use float(...) to ensure numeric type consistency
            avg_score = float(subj_results.aggregate(avg=Sum('average'))['avg'] / subj_results.count())
            subject_averages.append((subj.name, avg_score))

    if len(subject_averages) < 3:
        return None, {}, "Not enough subjects to form clusters."

    df = pd.DataFrame(subject_averages, columns=['Subject', 'AverageScore'])
    X = df[['AverageScore']].values

    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(X)
    df['Cluster'] = kmeans.labels_

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(x=df['AverageScore'], y=[0]*len(df), hue=df['Cluster'], palette='viridis', s=100, legend=True, ax=ax)
    for _, row in df.iterrows():
        ax.text(row['AverageScore'], 0.02, row['Subject'], rotation=45, ha='center', va='bottom', fontsize=9)

    ax.set_title("Subject Clusters by Average Performance (Out of 50)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Average Score (0-50)")
    ax.set_yticks([])

    cluster_chart = _figure_to_base64(fig)
    plt.close(fig)

    cluster_labels = dict(zip(df['Subject'], df['Cluster']))
    return cluster_chart, cluster_labels, None


############################################
# Class Performance Trends
############################################

def draw_class_performance_trends() -> Dict[str, Dict[str, Any]]:
    """
    Draw class performance trends over sessions, terms, and exams.
    All averages considered are out of 50.
    """
    classes = StudentClass.objects.all()
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    exams = ExamType.objects.all()

    class_insights: Dict[str, Dict[str, Any]] = {}

    for student_class in classes:
        results = Result.objects.filter(current_class=student_class).exclude(average__isnull=True)
        data = []
        for session in sessions:
            for term in terms:
                for exam in exams:
                    class_results = results.filter(session=session, term=term, exam=exam)
                    if not class_results.exists():
                        continue
                    student_overall_averages = []
                    distinct_students = class_results.values_list('student', flat=True).distinct()
                    for student_id in distinct_students:
                        student_res = class_results.filter(student_id=student_id)
                        if student_res.exists():
                            avg_per_student = float(student_res.aggregate(a=Sum('average'))['a'] / student_res.count())
                            student_overall_averages.append(avg_per_student)

                    if student_overall_averages:
                        class_overall_avg = sum(student_overall_averages) / len(student_overall_averages)
                        data.append({
                            'Session': session.name,
                            'Term': term.name,
                            'Exam': exam.name,
                            'Overall Average': class_overall_avg
                        })

        if not data:
            class_insights[student_class.name] = {
                'graph': None,
                'latest_average': None,
                'predicted_average': None,
                'comments_and_advice': "No performance data available for this class."
            }
            continue

        df = pd.DataFrame(data)
        # Convert to float to avoid any Decimal issues
        df['Overall Average'] = df['Overall Average'].astype(float)
        df['Index'] = range(len(df))
        latest_average = df['Overall Average'].iloc[-1]

        x = df['Index'].values.reshape(-1, 1)
        y = df['Overall Average'].values.reshape(-1, 1)
        model, model_type = use_advanced_model_if_possible(x, y)
        predicted_average = float(model.predict([[len(df)]])[0])

        comments_and_advice = (
            f"The class {student_class.name} is showing improvement. "
            f"Predicted next average: {predicted_average:.2f}/50."
            if predicted_average > latest_average else
            f"The class {student_class.name} may face a plateau or decline. "
            f"Predicted next average: {predicted_average:.2f}/50, lower than {latest_average:.2f}/50."
        )
        comments_and_advice += " Tailor teaching methods and resources accordingly."

        fig, ax = plt.subplots(figsize=(14, 7))
        sns.barplot(x='Session', y='Overall Average', hue='Exam', data=df, ci=None, ax=ax)
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel('Session', fontsize=12)
        ax.set_ylabel('Overall Average (Out of 50)', fontsize=12)
        ax.set_title(f'Performance Trends: {student_class.name} (Model: {model_type})', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        fig.tight_layout()

        image_base64 = _figure_to_base64(fig)
        plt.close(fig)

        class_insights[student_class.name] = {
            'graph': image_base64,
            'latest_average': latest_average,
            'predicted_average': predicted_average,
            'comments_and_advice': comments_and_advice
        }

    return class_insights


############################################
# Student Trends in Classes
############################################

def draw_student_trends_in_classes() -> Dict[str, Dict[int, Dict[str, Any]]]:
    """
    Draws performance trends for each student in their respective classes.
    Using average (out of 50) from the Result model directly.
    """
    classes = StudentClass.objects.all()
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    exams = ExamType.objects.all()
    trends_data: Dict[str, Dict[int, Dict[str, Any]]] = {}

    for student_class in classes:
        results = Result.objects.filter(current_class=student_class).exclude(average__isnull=True)
        students = results.values_list('student', flat=True).distinct()

        class_students_data: Dict[int, Dict[str, Any]] = {}
        for student_id in students:
            student_obj = Student.objects.filter(id=student_id).first()
            if not student_obj:
                continue

            student_data = []
            subject_overall_averages: Dict[str, List[float]] = {}

            for session in sessions:
                for term in terms:
                    for exam in exams:
                        student_results = results.filter(student=student_id, session=session, term=term, exam=exam)
                        if not student_results.exists():
                            continue
                        avg_scores = list(student_results.values_list('average', flat=True))
                        avg_scores = [float(v) for v in avg_scores if v is not None]
                        if avg_scores:
                            overall_average = sum(avg_scores) / len(avg_scores)
                            for r in student_results:
                                subj_name = r.subject.name
                                subject_overall_averages.setdefault(subj_name, []).append(float(r.average))
                            student_data.append({
                                'Session': session.name,
                                'Term': term.name,
                                'Exam': exam.name,
                                'Overall Average': overall_average,
                            })

            # Determine strongest, medium, weakest
            strongest_subjects, medium_subjects, weakest_subjects = [], [], []
            for subj, avgs in subject_overall_averages.items():
                avg = sum(avgs) / len(avgs)
                if avg > 40:  # Over 80%
                    strongest_subjects.append(subj)
                elif 25 < avg <= 40:
                    medium_subjects.append(subj)
                else:
                    weakest_subjects.append(subj)

            if student_data:
                df = pd.DataFrame(student_data)
                df['Session-Term-Exam'] = df['Session'] + " - " + df['Term'] + " - " + df['Exam']
                df['Overall Average'] = df['Overall Average'].astype(float)

                x = np.arange(len(df)).reshape(-1, 1)
                y = df['Overall Average'].values.reshape(-1, 1)

                if len(df) > 1:
                    model, _ = use_advanced_model_if_possible(x, y)
                    predicted_average = float(model.predict([[len(df)]])[0])
                else:
                    predicted_average = df['Overall Average'].iloc[-1]

                latest_average = df['Overall Average'].iloc[-1]
                over_and_over_average = df['Overall Average'].mean()

                comments_and_advice = generate_comments_and_advice(
                    over_and_over_average,
                    latest_average,
                    strongest_subjects,
                    medium_subjects,
                    weakest_subjects
                )

                fig, ax = plt.subplots(figsize=(14, 7))
                ax.bar(df['Session-Term-Exam'], df['Overall Average'], color='skyblue', alpha=0.7, label='Overall Average')
                ax.plot(df['Session-Term-Exam'], df['Overall Average'], marker='o', color='orange', label='Trend Line', linewidth=2)
                ax.tick_params(axis='x', rotation=45)
                ax.set_xlabel('Session - Term - Exam', fontsize=12)
                ax.set_ylabel('Overall Average (Out of 50)', fontsize=12)
                ax.set_title(
                    f"Performance Trends for {student_obj.firstname} {student_obj.middle_name} {student_obj.surname} in {student_class.name}", 
                    fontsize=14, fontweight='bold'
                )
                ax.legend(fontsize=10)
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                fig.tight_layout()

                image_base64 = _figure_to_base64(fig)
                plt.close(fig)

                class_students_data[student_id] = {
                    'name': f"{student_obj.firstname} {student_obj.middle_name} {student_obj.surname}",
                    'graph': image_base64,
                    'latest_average': latest_average,
                    'over_and_over_average': over_and_over_average,
                    'predicted_average': predicted_average,
                    'strongest_subjects': strongest_subjects,
                    'medium_subjects': medium_subjects,
                    'weakest_subjects': weakest_subjects,
                    'comments_and_advice': comments_and_advice,
                }

        if class_students_data:
            trends_data[student_class.name] = class_students_data

    return trends_data


############################################
# Subject Trends for Class
############################################

def draw_subject_trends_for_class() -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Draw time-series line graphs for each subject in each class.
    Returns a nested dictionary keyed by class name and subject name with their performance insights.
    """
    classes = StudentClass.objects.all()
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    exams = ExamType.objects.all()

    class_subject_insights: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for student_class in classes:
        results = Result.objects.filter(current_class=student_class)
        subject_ids = results.values_list('subject', flat=True).distinct()
        subjects = Subject.objects.filter(pk__in=subject_ids)

        subject_insights: Dict[str, Dict[str, Any]] = {}

        for subject in subjects:
            data = []
            for session in sessions:
                for term in terms:
                    for exam in exams:
                        subject_results = results.filter(session=session, term=term, exam=exam, subject=subject)
                        if not subject_results.exists():
                            continue
                        scores = []
                        for res in subject_results:
                            ts = res.test_score or Decimal('0')
                            es = res.exam_score or Decimal('0')
                            # Convert to float
                            total_score = float(ts) + float(es)
                            scores.append(total_score)
                        if scores:
                            avg_score = sum(scores) / len(scores)
                            data.append({
                                'Session': session.name,
                                'Term': term.name,
                                'Exam': exam.name,
                                'Average': avg_score
                            })

            if not data:
                subject_insights[subject.name] = {
                    'graph': None,
                    'latest_average': None,
                    'predicted_average': None,
                    'comments_and_advice': "No data available for this subject."
                }
                continue

            df = pd.DataFrame(data)
            df['Average'] = df['Average'].astype(float)
            df['Index'] = range(len(df))
            latest_average = df['Average'].iloc[-1]

            x = df['Index'].values.reshape(-1, 1)
            y = df['Average'].values.reshape(-1, 1)
            model, model_type = use_advanced_model_if_possible(x, y)
            predicted_average = float(model.predict([[len(df)]])[0])

            over_and_over_avg = df['Average'].mean()

            strongest_subjects, medium_subjects, weakest_subjects = [], [], []
            if over_and_over_avg > 80:
                strongest_subjects = [subject.name]
            elif over_and_over_avg > 50:
                medium_subjects = [subject.name]
            else:
                weakest_subjects = [subject.name]

            comments_and_advice = generate_comments_and_advice(
                over_and_over_avg, latest_average, strongest_subjects, medium_subjects, weakest_subjects
            )

            fig, ax = plt.subplots(figsize=(14, 7))
            x_labels = df['Session'] + "-" + df['Term'] + "-" + df['Exam']
            ax.bar(x_labels, df['Average'], color='skyblue', alpha=0.7, label='Average')
            ax.plot(x_labels, df['Average'], marker='o', color='orange', label='Trend Line', linewidth=2)
            ax.tick_params(axis='x', rotation=45)
            ax.set_xlabel('Session - Term - Exam', fontsize=12)
            ax.set_ylabel('Average Score', fontsize=12)
            ax.set_title(
                f"Subject Performance Trends for {subject.name} in {student_class.name} (Model: {model_type})",
                fontsize=14, fontweight='bold'
            )
            ax.legend(fontsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            fig.tight_layout()

            image_base64 = _figure_to_base64(fig)
            plt.close(fig)

            subject_insights[subject.name] = {
                'graph': image_base64,
                'latest_average': latest_average,
                'predicted_average': predicted_average,
                'comments_and_advice': comments_and_advice
            }

        class_subject_insights[student_class.name] = subject_insights

    return class_subject_insights


############################################
# Salary Distribution Charts
############################################

def draw_salary_distribution_charts() -> Tuple[
    Optional[str], Optional[str], Optional[str], Dict[str, float], List[Dict[str, Any]], float
]:
    """
    Generates salary distribution charts by occupation and staff members.
    Returns occupation chart, staff chart, error message, occupation distribution, staff distribution, and total salary.
    """
    staff_members = Staff.objects.filter(current_status="active")

    if not staff_members.exists():
        return None, None, "No active staff members to analyze.", {}, [], 0

    total_salary = staff_members.aggregate(total=Sum('salary'))['total'] or Decimal('0')
    if total_salary == 0:
        return None, None, "No salary data available to analyze.", {}, [], 0

    total_salary_float = float(total_salary)
    occupations = staff_members.values_list('occupation', flat=True).distinct()
    salary_by_occupation = {
        occupation: float(staff_members.filter(occupation=occupation).aggregate(total=Sum('salary'))['total'] or 0)
        for occupation in occupations
    }

    salary_by_staff = staff_members.values('firstname', 'middle_name', 'surname', 'salary').order_by('-salary')

    # Occupation chart
    occupation_labels = [o.title().replace("_", " ") for o in salary_by_occupation.keys()]
    occupation_percentages = [(s / total_salary_float) * 100 for s in salary_by_occupation.values()]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        occupation_percentages,
        labels=occupation_labels,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        colors=plt.cm.tab10.colors,
        startangle=90
    )
    ax.set_title("Salary Distribution by Occupation", fontsize=14, fontweight="bold")
    ax.axis('equal')
    occupation_chart = _figure_to_base64(fig)
    plt.close(fig)

    # Staff chart
    staff_percentages = [(float(s['salary']) / total_salary_float) * 100 for s in salary_by_staff]
    staff_labels = [f"{s['firstname']} {s['middle_name']} {s['surname']}" for s in salary_by_staff]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        staff_percentages,
        labels=staff_labels,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        colors=plt.cm.Set3.colors,
        startangle=90
    )
    ax.set_title("Salary Distribution by Staff", fontsize=14, fontweight="bold")
    ax.axis('equal')
    staff_chart = _figure_to_base64(fig)
    plt.close(fig)

    return occupation_chart, staff_chart, None, salary_by_occupation, list(salary_by_staff), total_salary_float


############################################
# Salary Variation Over Time
############################################

def draw_salary_variation_line_chart():
    """
    Plots the variation of total salary given each year-month.
    Returns a base64 graph, the salary data, and an error message if any.
    """
    salary_data = (
        SalaryInvoice.objects.values("month")
        .annotate(total_given_salary=Sum("total_given_salary"))
        .order_by("month")
    )

    if not salary_data.exists():
        return None, None, "No salary data available to analyze."

    months = [entry["month"].strftime("%Y-%m") for entry in salary_data]
    total_salaries = [float(entry["total_given_salary"] or 0) for entry in salary_data]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(months, total_salaries, marker="o", linestyle="-", color="blue", label="Total Given Salary")
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    ax.set_xlabel("Year-Month", fontsize=12)
    ax.set_ylabel("Total Given Salary", fontsize=12)
    ax.set_title("Variation of Total Salary Given Across Year-Month", fontsize=14, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(fontsize=10)
    fig.tight_layout()

    graph_base64 = _figure_to_base64(fig)
    plt.close(fig)

    return graph_base64, salary_data, None


############################################
# Expenditure Heatmap and Waterfall
############################################

def draw_expenditure_heatmap_and_waterfall() -> Tuple[
    Optional[str],
    Optional[str],
    Decimal,
    Dict[str, float],
    float,
    str,
    Optional[str]
]:
    """
    Generates an expenditure heatmap and waterfall chart for the current year.
    Returns heatmap, waterfall chart, total initial balance, category expenditures, remaining balance,
    trend description, and error message if any.
    """
    current_year = datetime.now().year
    expenditures = Expenditure.objects.filter(date__year=current_year)
    invoices = ExpenditureInvoice.objects.filter(date__year=current_year)

    if not expenditures.exists() or not invoices.exists():
        return None, None, Decimal('0'), {}, 0.0, "", "No expenditure or invoice data for the current year."

    total_initial_balance = invoices.aggregate(total=Sum('initial_balance'))['total'] or Decimal('0')
    total_initial_balance_float = float(total_initial_balance)

    category_data = (
        expenditures.values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )
    category_expenditures_dict = {item['category__name']: float(item['total_amount'] or 0) for item in category_data}

    total_spent = sum(category_expenditures_dict.values())
    remaining_balance = total_initial_balance_float - total_spent

    if remaining_balance > 0:
        trend_description = (
            f"Total expenditures: TZS {total_spent:,.2f}, leaving a surplus of TZS {remaining_balance:,.2f}. "
            "Financial management is good. Consider investing the surplus strategically."
        )
    elif remaining_balance < 0:
        trend_description = (
            f"Total expenditures: TZS {total_spent:,.2f} exceeded initial funds by "
            f"TZS {abs(remaining_balance):,.2f}. Immediate cost control measures needed."
        )
    else:
        trend_description = (
            f"Total expenditures matched initial balance (TZS {total_initial_balance_float:,.2f}). "
            "Spending was exact. Ensure some flexibility for unforeseen costs."
        )

    # Heatmap
    heatmap_base64 = None
    if category_expenditures_dict:
        df = pd.DataFrame(list(category_expenditures_dict.items()), columns=['Category', 'Total Amount'])
        pivot_df = df.set_index('Category')

        fig, ax = plt.subplots(figsize=(6, 6))
        sns.heatmap(pivot_df, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=0.5, cbar_kws={'label': 'Total Amount'}, ax=ax)
        ax.set_title("Expenditure Heatmap by Category", fontsize=16, fontweight="bold")
        fig.tight_layout()
        heatmap_base64 = _figure_to_base64(fig)
        plt.close(fig)

    # Waterfall Chart
    waterfall_base64 = None
    if total_initial_balance_float > 0:
        categories = list(category_expenditures_dict.keys()) + ['Remaining Balance']
        values = list(category_expenditures_dict.values()) + [remaining_balance]
        data = pd.DataFrame({'Category': categories, 'Values': values})
        data['Cumulative'] = data['Values'].cumsum()

        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['green' if v > 0 else 'red' for v in data['Values']]
        ax.bar(data['Category'], data['Values'], color=colors)
        ax.plot(data['Category'], data['Cumulative'], marker='o', color='blue', label='Cumulative')
        ax.set_title("Waterfall Chart of Expenditures", fontsize=16, fontweight="bold")
        ax.set_ylabel("Amount (TZS)")
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        fig.tight_layout()
        waterfall_base64 = _figure_to_base64(fig)
        plt.close(fig)

    return (heatmap_base64, waterfall_base64, total_initial_balance, category_expenditures_dict, 
            remaining_balance, trend_description, None)


############################################
# Profit Distribution
############################################

def generate_profit_pie_chart() -> Tuple[Optional[str], Optional[str]]:
    """
    Generates a pie chart showing profit distribution by source (Receipts vs. Uniform Sales) for the current session.
    Returns pie chart and error message.
    """
    current_session = AcademicSession.objects.filter(current=True).first()
    if not current_session:
        return None, "No current academic session available."

    total_receipts = Receipt.objects.filter(invoice__session=current_session).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
    total_uniforms = StudentUniform.objects.filter(session=current_session).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    total_receipts_float = float(total_receipts)
    total_uniforms_float = float(total_uniforms)
    overall_total = total_receipts_float + total_uniforms_float

    if overall_total == 0:
        return None, "No income data available for the current session."

    receipt_percentage = (total_receipts_float / overall_total) * 100 if overall_total > 0 else 0
    uniform_percentage = (total_uniforms_float / overall_total) * 100 if overall_total > 0 else 0

    labels = ['Receipts', 'Uniform Sales']
    percentages = [receipt_percentage, uniform_percentage]
    colors = ['#007bff', '#ffc107']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(percentages, labels=labels, autopct=lambda p: f'{p:.1f}%' if p > 0 else '', colors=colors, startangle=140)
    ax.set_title("Profit Distribution by Source", fontsize=14, fontweight='bold')
    ax.axis('equal')
    pie_chart_base64 = _figure_to_base64(fig)
    plt.close(fig)

    return pie_chart_base64, None


############################################
# Expenses Analysis
############################################

def draw_expenses_analysis() -> Tuple[
    Optional[str], Decimal, Decimal, Decimal, str
]:
    """
    Analyzes school expenses for the current session (salaries vs. other expenditures).
    Returns pie chart, total salaries, total expenditures, overall total, and comments.
    """
    current_session = AcademicSession.objects.filter(current=True).first()
    if not current_session:
        return None, Decimal('0'), Decimal('0'), Decimal('0'), "No active session available for analysis."

    total_salaries = SalaryInvoice.objects.filter(session=current_session).aggregate(total=Sum('total_given_salary'))['total'] or Decimal('0')
    total_expenditures = ExpenditureInvoice.objects.filter(session=current_session).aggregate(total=Sum('initial_balance'))['total'] or Decimal('0')

    overall_total = total_salaries + total_expenditures
    if overall_total == 0:
        return None, total_salaries, total_expenditures, overall_total, "No expenses recorded for this session."

    total_salaries_float = float(total_salaries)
    total_expenditures_float = float(total_expenditures)
    overall_total_float = float(overall_total)

    data = {
        'Salaries': total_salaries_float,
        'Expenditures': total_expenditures_float,
    }
    sizes = [(v / overall_total_float) * 100 for v in data.values()]
    labels = list(data.keys())
    colors = ['#FF6384', '#36A2EB']

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        textprops={'fontsize': 12}
    )
    ax.set_title(f"Expenses Distribution for {current_session.name}", fontsize=14, fontweight="bold")
    fig.tight_layout()

    pie_chart = _figure_to_base64(fig)
    plt.close(fig)

    if total_salaries_float > total_expenditures_float:
        comments = (
            f"Salaries dominate expenses in {current_session.name}. "
            "Consider optimizing payroll or increasing revenue streams."
        )
    elif total_expenditures_float > total_salaries_float:
        comments = (
            f"Non-salary expenditures dominate {current_session.name}. "
            "Explore cost-saving measures in operations and supplies."
        )
    else:
        comments = (
            f"Salaries and other expenses are balanced in {current_session.name}. "
            "Maintain this harmony, but stay alert for cost overruns."
        )

    return pie_chart, total_salaries, total_expenditures, overall_total, comments


############################################
# Linear Regression Graph for Financial Trends
############################################

def draw_linear_regression_graph() -> Tuple[
    Optional[str],
    List[Tuple[str, float, float, float]],
    float,
    float,
    float,
    str
]:
    """
    Draws a linear regression graph for the school's balance trends across sessions.
    Returns a regression graph (base64), balance data, predicted profit, predicted expenses, predicted balance, and comments.
    """
    sessions = AcademicSession.objects.all().order_by('id')
    if not sessions.exists():
        return None, [], 0, 0, 0, "No session data available."

    balance_data = []
    for session in sessions:
        total_receipts = Receipt.objects.filter(invoice__session=session).aggregate(sum=Sum('amount_paid'))['sum'] or 0
        total_uniforms = StudentUniform.objects.filter(session=session).aggregate(sum=Sum('amount'))['sum'] or 0
        total_income = float(total_receipts) + float(total_uniforms)

        total_salaries = SalaryInvoice.objects.filter(session=session).aggregate(sum=Sum('total_given_salary'))['sum'] or 0
        total_expenditure_invoices = ExpenditureInvoice.objects.filter(session=session).aggregate(sum=Sum('initial_balance'))['sum'] or 0
        total_expenses = float(total_salaries) + float(total_expenditure_invoices)

        balance = total_income - total_expenses
        if total_income > 0 or total_expenses > 0:
            balance_data.append((session.name, balance, total_income, total_expenses))

    if not balance_data:
        return None, [], 0, 0, 0, "No financial data found in any sessions."

    if len(balance_data) == 1:
        session_name, balance, profit, expenses = balance_data[0]
        predicted_profit = profit
        predicted_expenses = expenses
        predicted_balance = balance

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter([session_name], [balance], color='blue', label='Actual Balance')
        ax.axhline(y=balance, color='red', linestyle='--', label='Flat Trend')
        ax.set_title('Balance Trends Across Sessions', fontsize=14, fontweight='bold')
        ax.set_xlabel('Session')
        ax.set_ylabel('Balance (TZS)')
        ax.legend()
        ax.grid(True)
        fig.tight_layout()

        regression_graph = _figure_to_base64(fig)
        plt.close(fig)

        regression_comments = (
            f"Only one session ({session_name}) of data. Current balance: {balance:,.2f} TZS. "
            "No trend can be established yet."
        )
        return regression_graph, balance_data, predicted_profit, predicted_expenses, predicted_balance, regression_comments

    df = pd.DataFrame(balance_data, columns=['Session', 'Balance', 'Profit', 'Expenses'])
    df['Session_Number'] = range(1, len(df) + 1)
    df['Balance'] = df['Balance'].astype(float)
    df['Profit'] = df['Profit'].astype(float)
    df['Expenses'] = df['Expenses'].astype(float)

    x = df['Session_Number'].values.reshape(-1, 1)
    y = df['Balance'].values.reshape(-1, 1)

    model, _ = use_advanced_model_if_possible(x, y)
    slope = model.predict([[len(df)]])[0] - model.predict([[len(df)-1]])[0]

    next_session_number = len(df) + 1
    predicted_balance = float(model.predict([[next_session_number]])[0][0])
    predicted_profit = df['Profit'].iloc[-1]
    predicted_expenses = df['Expenses'].iloc[-1]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(df['Session'], df['Balance'], color='blue', label='Actual Balances')
    ax.plot(df['Session'], model.predict(x), color='red', linestyle='--', label='Trend Line')
    ax.axhline(0, color='gray', linewidth=1, linestyle='--')
    ax.set_title('Balance Trends Across Sessions', fontsize=16, fontweight='bold')
    ax.set_xlabel('Session')
    ax.set_ylabel('Balance (TZS)')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    fig.tight_layout()

    regression_graph = _figure_to_base64(fig)
    plt.close(fig)

    slope_value = float(slope)
    if slope_value > 0:
        regression_comments = (
            f"Positive trend ({slope_value:.2f}/session): Financial health is improving. "
            "Maintain strategies for revenue growth and cost control."
        )
    elif slope_value < 0:
        regression_comments = (
            f"Negative trend ({slope_value:.2f}/session): Financial health is declining. "
            "Consider immediate measures to cut costs and boost income."
        )
    else:
        regression_comments = (
            "Stable trend: No significant change. Aim for improvement through careful planning."
        )

    return regression_graph, balance_data, predicted_profit, predicted_expenses, predicted_balance, regression_comments

