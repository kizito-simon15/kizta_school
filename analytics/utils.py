import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from apps.result.models import Result
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass

def generate_advice_and_comments(overall_average):
    """
    Generate descriptive and flexible comments and advice based on the overall average.
    """
    if overall_average < 5:
        return (
            "The overall average for this class is critically low. This indicates a severe issue with the learning "
            "process. Immediate action is required. Suggestions include:\n"
            "- Introducing remedial classes to revisit fundamental concepts.\n"
            "- Conducting regular assessments to identify areas where students are struggling.\n"
            "- Increasing engagement with parents to provide support at home.\n"
            "- Encouraging teachers to adopt interactive and student-friendly teaching methods.\n"
            "Addressing these issues quickly can help to set the class on the right path to improvement."
        )
    elif overall_average < 15:
        return (
            "This performance is below average and reflects gaps in understanding or consistency in learning. To improve:\n"
            "- Focus on creating small, manageable study groups for peer-to-peer learning.\n"
            "- Ensure that teachers provide detailed feedback on assignments and tests.\n"
            "- Utilize creative teaching aids like videos, charts, and real-life examples to simplify concepts.\n"
            "- Motivate students by setting achievable goals and rewarding progress.\n"
            "With consistent effort, the class can begin to show significant improvement."
        )
    elif overall_average < 25:
        return (
            "The performance is still low, though progress might be visible. At this stage, the class needs to:\n"
            "- Maintain steady effort and focus on bridging knowledge gaps.\n"
            "- Ensure teachers conduct more regular quizzes and provide personalized feedback.\n"
            "- Implement a reward system to encourage better performance among students.\n"
            "- Engage with parents to provide a supportive learning environment at home.\n"
            "With continued focus and consistent study habits, this class has the potential to improve further."
        )
    elif overall_average < 35:
        return (
            "The class is performing at an average level. While this is a stable position, there is room for improvement:\n"
            "- Encourage students to take more initiative in their studies, such as self-study or extra reading.\n"
            "- Continue with regular tests and feedback sessions to track progress.\n"
            "- Motivate the class with activities like academic competitions or debates.\n"
            "- Ensure that all students participate actively in lessons.\n"
            "This level is good, but with some additional effort, the class can achieve excellence."
        )
    elif overall_average < 45:
        return (
            "This is a commendable performance, showing that the class is nearing excellence. Suggestions to maintain and improve:\n"
            "- Regularly revise and test knowledge to ensure retention and understanding.\n"
            "- Introduce advanced concepts to challenge and engage students further.\n"
            "- Foster collaboration between students for shared learning experiences.\n"
            "- Encourage teachers to continue their effective methods and provide ongoing support.\n"
            "The class is on the right track, and with sustained effort, it can achieve the highest marks."
        )
    elif overall_average < 50:
        return (
            "Congratulations on achieving high marks! This is an excellent performance. To maintain this level:\n"
            "- Ensure that students remain motivated and enthusiastic about learning.\n"
            "- Introduce enrichment programs like STEM projects or advanced workshops.\n"
            "- Celebrate successes to keep morale high among students and teachers.\n"
            "- Encourage students to mentor peers in other classes, which will reinforce their own learning.\n"
            "Keep up the great work, and continue striving for perfection."
        )
    else:
        return (
            "Outstanding performance! The class has achieved the highest possible marks. To maintain this excellence:\n"
            "- Continue with the strategies that have proven successful so far.\n"
            "- Encourage students to explore new areas of learning beyond the curriculum.\n"
            "- Introduce leadership opportunities for students to inspire others.\n"
            "- Provide advanced-level material and activities to keep the momentum going.\n"
            "Maintaining this level is challenging, but with dedication, the class can consistently perform at the top level."
        )


def draw_class_performance_trends():
    """
    Draws graphs showing the trends of overall averages for all classes across session terms and exam types.
    Each class gets a separate graph and accompanying insights.
    Returns a dictionary with the class name as key and a dictionary of graph and insights as value.
    """
    classes = StudentClass.objects.all()
    class_insights = {}

    for student_class in classes:
        # Query results for the given class
        results = Result.objects.filter(current_class=student_class)

        # Prepare data for the graph
        data = []
        for session in AcademicSession.objects.all():
            for term in AcademicTerm.objects.all():
                for exam in ExamType.objects.all():
                    # Filter results for the given session, term, and exam type
                    class_results = results.filter(session=session, term=term, exam=exam)

                    if class_results.exists():
                        # Calculate overall average for each student in the class
                        student_overall_averages = []
                        for student_id in class_results.values_list('student', flat=True).distinct():
                            # Get all subjects for the student in this session-term-exam
                            student_results = class_results.filter(student_id=student_id)

                            if student_results.exists():
                                # Calculate average per subject
                                subject_averages = []
                                for res in student_results:
                                    if res.test_score is not None and res.exam_score is not None:
                                        subject_average = (res.test_score + res.exam_score) / 2
                                    elif res.test_score is not None:
                                        subject_average = res.test_score
                                    elif res.exam_score is not None:
                                        subject_average = res.exam_score
                                    else:
                                        subject_average = 0
                                    subject_averages.append(subject_average)

                                # Calculate overall average per student
                                if subject_averages:
                                    overall_average_per_student = sum(subject_averages) / len(subject_averages)
                                    student_overall_averages.append(overall_average_per_student)

                        # Calculate the overall average for the class in this session, term, and exam
                        if student_overall_averages:
                            class_overall_average = sum(student_overall_averages) / len(student_overall_averages)
                            data.append({
                                'Session': session.name,
                                'Term': term.name,
                                'Exam': exam.name,
                                'Overall Average': class_overall_average
                            })

        # Convert data to a DataFrame for analysis and plotting
        if data:
            df = pd.DataFrame(data)
            df['Session-Term-Exam'] = df['Session'] + " - " + df['Term'] + " - " + df['Exam']

            # Latest and Predicted Averages
            latest_average = df['Overall Average'].iloc[-1] if not df.empty else None
            predicted_average = (
                latest_average + (latest_average - df['Overall Average'].iloc[-2])
                if len(df) > 1 else latest_average
            )

            # Generate Comments and Advice
            comments_and_advice = generate_advice_and_comments(latest_average)

            # Create the plot
            plt.figure(figsize=(14, 7))
            plt.bar(df['Session-Term-Exam'], df['Overall Average'], color='#1f77b4', alpha=0.8, label='Overall Average')
            plt.plot(df['Session-Term-Exam'], df['Overall Average'], marker='o', color='#ff7f0e', label='Trend Line', linewidth=2)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            plt.xlabel('Session - Term - Exam', fontsize=12)
            plt.ylabel('Overall Average', fontsize=12)
            plt.title(f'Performance Trends: {student_class.name}', fontsize=14, fontweight='bold')
            plt.legend(fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()

            # Save the graph to a base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            plt.close()

            # Store insights
            class_insights[student_class.name] = {
                'graph': image_base64,
                'latest_average': latest_average,
                'predicted_average': predicted_average,
                'comments_and_advice': comments_and_advice,
            }

    return class_insights

def generate_subject_advice_and_comments(overall_average):
    """
    Generate descriptive comments and advice for a subject based on its overall average.
    """
    if overall_average < 5:
        return (
            "The overall average for this subject is critically low. It suggests severe difficulties in comprehension. "
            "Immediate steps include:\n"
            "- Extra support classes for foundational concepts.\n"
            "- One-on-one tutoring to address specific challenges.\n"
            "- Interactive teaching methods to engage students more effectively."
        )
    elif overall_average < 15:
        return (
            "This subject's performance is low. Students may need targeted practice. Recommendations:\n"
            "- Use practice exercises and regular tests to reinforce learning.\n"
            "- Provide detailed feedback to guide improvement.\n"
            "- Focus on simplifying complex topics with visual aids or real-life examples."
        )
    elif overall_average < 25:
        return (
            "The performance in this subject is below average. To enhance results:\n"
            "- Conduct group discussions and collaborative activities to encourage peer learning.\n"
            "- Assign more homework and monitor progress closely.\n"
            "- Schedule regular revision sessions to strengthen retention."
        )
    elif overall_average < 35:
        return (
            "The subject is performing at an average level. To maintain and improve:\n"
            "- Encourage consistent participation and self-study among students.\n"
            "- Provide additional materials like summaries and key points for revision.\n"
            "- Introduce competitive activities like quizzes to make learning engaging."
        )
    elif overall_average < 45:
        return (
            "The subject performance is good and approaching excellence. Suggestions:\n"
            "- Explore advanced topics to challenge students and keep them engaged.\n"
            "- Reward good performance to maintain motivation.\n"
            "- Continue regular assessments to track and refine progress."
        )
    elif overall_average < 50:
        return (
            "Excellent performance in this subject! To sustain this level:\n"
            "- Maintain regular study habits and encourage group discussions.\n"
            "- Introduce enrichment programs like workshops or guest lectures.\n"
            "- Celebrate achievements to keep morale high."
        )
    else:
        return (
            "Outstanding performance in this subject! To ensure continued excellence:\n"
            "- Focus on advanced applications and research-oriented projects.\n"
            "- Encourage students to assist peers in other classes.\n"
            "- Recognize both teachers and students for their efforts."
        )


from apps.corecode.models import Subject

def draw_subject_trends_for_class():
    """
    Draws time-series line graphs for each subject in each class.
    Shows trends of subject-level overall averages across session terms and exams.
    Provides insights including latest and predicted overall averages, along with comments and advice.
    """
    classes = StudentClass.objects.all()
    class_subject_insights = {}

    for student_class in classes:
        # Query all subjects studied in the class
        subjects = Result.objects.filter(current_class=student_class).values_list('subject', flat=True).distinct()
        subjects = [Subject.objects.get(pk=subject_id) for subject_id in subjects]
        subject_insights = {}

        for subject in subjects:
            # Query results for the given subject in the given class
            results = Result.objects.filter(current_class=student_class, subject=subject)

            # Prepare data for the graph
            data = []
            for session in AcademicSession.objects.all():
                for term in AcademicTerm.objects.all():
                    for exam in ExamType.objects.all():
                        # Filter results for the given session, term, and exam
                        subject_results = results.filter(session=session, term=term, exam=exam)

                        if subject_results.exists():
                            # Calculate the overall average for the subject in the class
                            subject_averages = [res.average for res in subject_results if res.average is not None]
                            if subject_averages:
                                overall_average = sum(subject_averages) / len(subject_averages)
                                data.append({
                                    'Session': session.name,
                                    'Term': term.name,
                                    'Exam': exam.name,
                                    'Overall Average': overall_average
                                })

            # Convert data to a DataFrame for plotting and analysis
            if data:
                df = pd.DataFrame(data)
                df['Session-Term-Exam'] = df['Session'] + " - " + df['Term'] + " - " + df['Exam']

                # Latest and Predicted Averages
                latest_average = df['Overall Average'].iloc[-1] if not df.empty else None
                predicted_average = (
                    latest_average + (latest_average - df['Overall Average'].iloc[-2])
                    if len(df) > 1 else latest_average
                )

                # Generate Comments and Advice
                comments_and_advice = generate_subject_advice_and_comments(latest_average)

                # Create the plot
                plt.figure(figsize=(14, 7))
                plt.plot(df['Session-Term-Exam'], df['Overall Average'], marker='o', color='#4a90e2', linewidth=2)
                plt.xticks(rotation=45, ha='right', fontsize=10)
                plt.yticks(fontsize=10)
                plt.xlabel('Session - Term - Exam', fontsize=12)
                plt.ylabel('Overall Average', fontsize=12)
                plt.title(f'Trends for {subject.name} in Class {student_class.name}', fontsize=14, fontweight='bold')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()

                # Save the graph to a base64 string
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close()

                # Store insights
                subject_insights[subject.name] = {
                    'graph': image_base64,
                    'latest_average': latest_average,
                    'predicted_average': predicted_average,
                    'comments_and_advice': comments_and_advice,
                }

        # Add all subject insights for the class
        class_subject_insights[student_class.name] = subject_insights

    return class_subject_insights

import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from apps.result.models import Result
from apps.corecode.models import AcademicSession, AcademicTerm, ExamType, StudentClass
from apps.students.models import Student

from apps.students.models import Student
from apps.corecode.models import Subject

def draw_student_trends_in_classes():
    """
    Draws performance trends for each student in their respective classes.
    Displays overall averages of the student in all session-term-exams.
    Also calculates strongest, medium, and weakest subjects for each student.
    """
    classes = StudentClass.objects.all()
    trends_data = {}

    for student_class in classes:
        # Query results for the given class
        results = Result.objects.filter(current_class=student_class)
        students = results.values_list('student', flat=True).distinct()

        class_students_data = {}

        for student_id in students:
            # Get the student object
            student = Student.objects.filter(id=student_id).first()

            if not student:
                continue

            # Prepare data for the graph
            student_data = []
            subject_overall_averages = {}  # For subject trends

            for session in AcademicSession.objects.all():
                for term in AcademicTerm.objects.all():
                    for exam in ExamType.objects.all():
                        # Filter results for the student in the given session, term, and exam
                        student_results = results.filter(student=student_id, session=session, term=term, exam=exam)

                        if student_results.exists():
                            # Calculate overall average for the student in this session, term, exam
                            subject_averages = []
                            for res in student_results:
                                if res.test_score is not None and res.exam_score is not None:
                                    subject_average = (res.test_score + res.exam_score) / 2
                                elif res.test_score is not None:
                                    subject_average = res.test_score
                                elif res.exam_score is not None:
                                    subject_average = res.exam_score
                                else:
                                    subject_average = 0

                                subject_averages.append(subject_average)

                                # Update subject overall average
                                if res.subject.name not in subject_overall_averages:
                                    subject_overall_averages[res.subject.name] = []
                                subject_overall_averages[res.subject.name].append(subject_average)

                            if subject_averages:
                                overall_average = sum(subject_averages) / len(subject_averages)
                                student_data.append({
                                    'Session': session.name,
                                    'Term': term.name,
                                    'Exam': exam.name,
                                    'Overall Average': overall_average,
                                })

            # Calculate strongest, medium, and weakest subjects
            strongest_subjects = []
            medium_subjects = []
            weakest_subjects = []

            for subject, averages in subject_overall_averages.items():
                over_and_over_subject_average = sum(averages) / len(averages)

                if over_and_over_subject_average > 40:
                    strongest_subjects.append(subject)
                elif 30 < over_and_over_subject_average <= 40:
                    medium_subjects.append(subject)
                elif over_and_over_subject_average <= 29:
                    weakest_subjects.append(subject)

            # Create DataFrame and plot the graph
            if student_data:
                df = pd.DataFrame(student_data)
                df['Session-Term-Exam'] = df['Session'] + " - " + df['Term'] + " - " + df['Exam']

                # Plot the graph
                plt.figure(figsize=(14, 7))
                plt.bar(df['Session-Term-Exam'], df['Overall Average'], color='skyblue', alpha=0.7, label='Overall Average')
                plt.plot(df['Session-Term-Exam'], df['Overall Average'], marker='o', color='orange', label='Trend Line', linewidth=2)
                plt.xticks(rotation=45, ha='right')
                plt.xlabel('Session - Term - Exam', fontsize=12)
                plt.ylabel('Overall Average', fontsize=12)
                plt.title(f"Performance Trends for {student.firstname} {student.middle_name} {student.surname} in Class: {student_class.name}", fontsize=14, fontweight='bold')
                plt.legend(fontsize=10)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()

                # Save the graph to a base64 string
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close()

                # Calculate the latest overall average
                latest_average = df['Overall Average'].iloc[-1]

                # Calculate the over-and-over average
                over_and_over_average = df['Overall Average'].mean()

                # Predict the next overall average
                predicted_average = latest_average + (latest_average - df['Overall Average'].iloc[-2]) if len(df) > 1 else latest_average

                # Generate comments and advice
                comments_and_advice = generate_comments_and_advice(
                    over_and_over_average, latest_average, strongest_subjects, medium_subjects, weakest_subjects
                )

                # Add data to the class students dictionary
                class_students_data[student.id] = {
                    'name': f"{student.firstname} {student.middle_name} {student.surname}",
                    'graph': image_base64,
                    'latest_average': latest_average,
                    'over_and_over_average': over_and_over_average,
                    'predicted_average': predicted_average,
                    'strongest_subjects': strongest_subjects,
                    'medium_subjects': medium_subjects,
                    'weakest_subjects': weakest_subjects,
                    'comments_and_advice': comments_and_advice,
                }

        # Add student data to the class trends data
        if class_students_data:
            trends_data[student_class.name] = class_students_data

    return trends_data


def generate_comments_and_advice(over_and_over_average, latest_average, strongest, medium, weakest):
    """
    Generate comments and advice based on over-and-over average and latest average, 
    as well as subject trends.
    """
    advice = []

    # General performance trends
    if over_and_over_average < 5:
        advice.append(
            f"The overall performance is critically low (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) confirms this. Immediate intervention is needed."
        )
    elif over_and_over_average < 15:
        advice.append(
            f"The performance is below average (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) shows some progress. Encourage more focused study sessions."
        )
    elif over_and_over_average < 25:
        advice.append(
            f"The performance is slightly below average (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) shows room for improvement. Structured support and assessments can help."
        )
    elif over_and_over_average < 35:
        advice.append(
            f"The performance is average (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) shows steady progress. Consistency is key."
        )
    elif over_and_over_average < 45:
        advice.append(
            f"The performance is strong (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) reflects great effort. Keep striving for excellence."
        )
    else:
        advice.append(
            f"Excellent performance! (Over-and-over average: {over_and_over_average:.2f}). "
            f"The latest performance ({latest_average:.2f}) shows outstanding consistency. Maintain this momentum!"
        )

    # Subject trends
    if strongest:
        advice.append(
            f"Congratulations on your strongest subjects: {', '.join(strongest)}. Keep up the excellent performance in these areas."
        )
    if medium:
        advice.append(
            f"The medium subjects ({', '.join(medium)}) show room for growth. Focus on improving your understanding in these areas."
        )
    if weakest:
        advice.append(
            f"The weakest subjects ({', '.join(weakest)}) require immediate attention. Seek help, review fundamentals, and practice regularly."
        )

    return " ".join(advice)

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def draw_class_regression_trends():
    """
    Draws regression graphs for each student in their respective classes.
    Categorizes students based on the slope of the regression line and overall performance.
    Ensures no duplication in group assignments.
    Returns a dictionary with class names as keys and another dictionary of student details as values.
    """
    classes = StudentClass.objects.all()
    trends_data = {}

    for student_class in classes:
        results = Result.objects.filter(current_class=student_class)
        students = results.values_list('student', flat=True).distinct()

        class_students_data = {}
        positive_trend = []
        constant_trend = []
        negative_trend = []
        danger_students = []
        medium_students = []
        excellent_students = []

        for student_id in students:
            student = Student.objects.filter(id=student_id).first()

            if not student:
                continue

            student_data = []
            for session in AcademicSession.objects.all():
                for term in AcademicTerm.objects.all():
                    for exam in ExamType.objects.all():
                        student_results = results.filter(student=student_id, session=session, term=term, exam=exam)

                        if student_results.exists():
                            subject_averages = []
                            for res in student_results:
                                if res.test_score is not None and res.exam_score is not None:
                                    subject_average = (res.test_score + res.exam_score) / 2
                                elif res.test_score is not None:
                                    subject_average = res.test_score
                                elif res.exam_score is not None:
                                    subject_average = res.exam_score
                                else:
                                    subject_average = 0
                                subject_averages.append(subject_average)

                            if subject_averages:
                                overall_average = sum(subject_averages) / len(subject_averages)
                                student_data.append(overall_average)

            if student_data:
                # Generate x-axis values (e.g., exam indices)
                x_values = np.arange(len(student_data)).reshape(-1, 1)
                y_values = np.array(student_data).reshape(-1, 1)

                # Perform linear regression
                model = LinearRegression()
                model.fit(x_values, y_values)
                slope = model.coef_[0][0]  # Slope of the regression line

                # Calculate over-and-over trend average
                over_and_over_average = sum(student_data) / len(student_data)

                # Plot the graph
                plt.figure(figsize=(10, 5))
                plt.scatter(x_values, y_values, color='blue', label='Overall Average (dots)')
                plt.plot(x_values, model.predict(x_values), color='red', linewidth=2, label='Regression Line')
                plt.title(f"Regression Trend for {student.firstname} {student.middle_name} {student.surname}")
                plt.xlabel('Session-Term-Exam Index')
                plt.ylabel('Overall Average')
                plt.legend()
                plt.grid()
                plt.tight_layout()

                # Save the graph to a base64 string
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close()

                # Categorize based on slope
                if slope > 0:
                    slope_category = "Positive Trend"
                    positive_trend.append(f"{student.firstname} {student.middle_name} {student.surname}")
                elif slope < 0:
                    slope_category = "Negative Trend"
                    negative_trend.append(f"{student.firstname} {student.middle_name} {student.surname}")
                else:
                    slope_category = "Constant Trend"
                    constant_trend.append(f"{student.firstname} {student.middle_name} {student.surname}")

                # Categorize based on over-and-over average
                if over_and_over_average < 25:
                    danger_students.append(f"{student.firstname} {student.middle_name} {student.surname}")
                    advice = (
                        "Your performance is critically low. Focus on understanding core concepts, seek help from teachers, "
                        "and participate actively in revision sessions to improve."
                    )
                elif over_and_over_average < 41:
                    medium_students.append(f"{student.firstname} {student.middle_name} {student.surname}")
                    advice = (
                        "Your performance is at a medium level. Continue working steadily, focus on weak areas, and aim for more consistency in your studies."
                    )
                else:
                    excellent_students.append(f"{student.firstname} {student.middle_name} {student.surname}")
                    advice = (
                        "Congratulations on your excellent performance! Keep up the good work, continue challenging yourself, "
                        "and help your peers for collective success."
                    )

                # Add data to the class students dictionary
                class_students_data[student.id] = {
                    'name': f"{student.firstname} {student.middle_name} {student.surname}",
                    'graph': image_base64,
                    'slope_category': slope_category,
                    'over_and_over_average': over_and_over_average,
                    'advice': advice,
                }

        # Ensure no duplication in group assignments
        positive_trend = list(set(positive_trend))
        constant_trend = list(set(constant_trend))
        negative_trend = list(set(negative_trend))
        danger_students = list(set(danger_students))
        medium_students = list(set(medium_students))
        excellent_students = list(set(excellent_students))

        # Add trend data to the dictionary
        if class_students_data:
            trends_data[student_class.name] = {
                'students': class_students_data,
                'positive_trend': positive_trend,
                'constant_trend': constant_trend,
                'negative_trend': negative_trend,
                'danger_students': danger_students,
                'medium_students': medium_students,
                'excellent_students': excellent_students,
            }

    return trends_data

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from apps.staffs.models import Staff
from django.db import models

def draw_salary_distribution_charts():
    """
    Generates two pie charts:
    1. Salary distribution by occupation.
    2. Salary distribution by individual staff.
    Returns both pie charts as base64 encoded strings, salary details by occupation, 
    salary details by staff, and total salary.
    """
    staff_members = Staff.objects.filter(current_status="active")
    
    if not staff_members.exists():
        return None, None, "No active staff members to analyze.", {}, {}, 0

    # Total salary
    total_salary = staff_members.aggregate(total=models.Sum('salary'))['total'] or 0

    if total_salary == 0:
        return None, None, "No salary data available to analyze.", {}, {}, 0

    # Salary by occupation
    occupations = staff_members.values_list('occupation', flat=True).distinct()
    salary_by_occupation = {
        occupation: staff_members.filter(occupation=occupation).aggregate(total=models.Sum('salary'))['total'] or 0
        for occupation in occupations
    }

    # Salary by staff
    salary_by_staff = staff_members.values('firstname', 'middle_name', 'surname', 'salary').order_by('-salary')

    # Generate Pie Chart for Occupations
    occupation_labels = [occupation.title().replace("_", " ") for occupation in salary_by_occupation.keys()]
    occupation_percentages = [
        (salary / total_salary) * 100 for salary in salary_by_occupation.values()
    ]
    plt.figure(figsize=(6, 6))
    plt.pie(
        occupation_percentages,
        labels=occupation_labels,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        colors=plt.cm.tab10.colors,
        startangle=90,
    )
    plt.title("Salary Distribution by Occupation", fontsize=14, fontweight="bold")
    plt.axis('equal')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    occupation_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Generate Pie Chart for Staff
    staff_labels = [
        f"{staff['firstname']} {staff['middle_name']} {staff['surname']}" for staff in salary_by_staff
    ]
    staff_percentages = [
        (staff['salary'] / total_salary) * 100 for staff in salary_by_staff
    ]
    plt.figure(figsize=(6, 6))
    plt.pie(
        staff_percentages,
        labels=staff_labels,
        autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
        colors=plt.cm.Set3.colors,
        startangle=90,
    )
    plt.title("Salary Distribution by Staff", fontsize=14, fontweight="bold")
    plt.axis('equal')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    staff_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return occupation_chart, staff_chart, None, salary_by_occupation, salary_by_staff, total_salary

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models import Sum
from apps.finance.models import SalaryInvoice

def draw_salary_variation_line_chart():
    """
    Calculates the overall total salary given each year-month and plots a line graph.
    Returns the graph as a base64 encoded string and salary data for each year-month.
    """
    # Query SalaryInvoices and group by year-month
    salary_data = (
        SalaryInvoice.objects.values("month")
        .annotate(total_given_salary=Sum("total_given_salary"))
        .order_by("month")
    )

    if not salary_data.exists():
        return None, "No salary data available to analyze."

    # Prepare data for the graph
    months = [entry["month"].strftime("%Y-%m") for entry in salary_data]
    total_salaries = [entry["total_given_salary"] for entry in salary_data]

    # Plot the line graph
    plt.figure(figsize=(10, 6))
    plt.plot(months, total_salaries, marker="o", linestyle="-", color="blue", label="Total Given Salary")
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.xlabel("Year-Month", fontsize=12)
    plt.ylabel("Total Given Salary", fontsize=12)
    plt.title("Variation of Total Salary Given Across Year-Month", fontsize=14, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Convert the graph to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    graph_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close()

    return graph_base64, salary_data

import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import seaborn as sns
from expenditures.models import Category, Expenditure, ExpenditureInvoice
from datetime import datetime
from django.db.models import Sum

from decimal import Decimal
from django.db.models import Sum
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import seaborn as sns
from expenditures.models import Expenditure, ExpenditureInvoice

def draw_expenditure_heatmap_and_waterfall():
    """
    Generates a heatmap of expenditures by category and a waterfall chart showing how the expenditure invoice was spent.
    Returns:
        - Heatmap as a base64 string.
        - Waterfall chart as a base64 string.
        - Total initial balance.
        - Total expenditures by category.
        - Remaining balance.
        - Description and advice for the trend.
        - Error message (if any).
    """
    current_year = datetime.now().year

    # Filter expenditures and invoices for the current year
    expenditures = Expenditure.objects.filter(date__year=current_year)
    invoices = ExpenditureInvoice.objects.filter(date__year=current_year)

    # Check if there are expenditures or invoices
    if not expenditures.exists() or not invoices.exists():
        return None, None, Decimal('0'), {}, Decimal('0'), "No expenditure or invoice data available for the current year.", None

    # Total initial balance
    total_initial_balance = invoices.aggregate(total=Sum('initial_balance'))['total'] or Decimal('0')

    # Total expenditures by category
    category_expenditures = (
        expenditures.values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )
    category_expenditures_dict = {
        item['category__name']: float(item['total_amount']) for item in category_expenditures
    }

    # Remaining balance
    total_spent = sum(category_expenditures_dict.values())
    remaining_balance = float(total_initial_balance) - total_spent

    # Generate description and advice
    if remaining_balance > 0:
        trend_description = (
            f"In the year {current_year}, the total expenditures amounted to TZS {total_spent:,.2f}, "
            f"leaving a positive balance of TZS {remaining_balance:,.2f}. This indicates good financial management. "
            "Consider reallocating the remaining funds towards future planning or investments."
        )
    elif remaining_balance < 0:
        trend_description = (
            f"In the year {current_year}, the total expenditures amounted to TZS {total_spent:,.2f}, "
            f"which exceeded the initial balance by TZS {abs(remaining_balance):,.2f}. This results in a deficit. "
            "Immediate action is needed to either reduce spending in certain categories or increase funding sources."
        )
    else:
        trend_description = (
            f"In the year {current_year}, the total expenditures exactly matched the initial balance (TZS {total_initial_balance:,.2f}), "
            "leaving no remaining funds. While this shows efficient spending, ensure adequate planning for unforeseen expenses."
        )

    # Heatmap preparation
    heatmap_base64 = None
    if category_expenditures_dict:
        df = pd.DataFrame(
            list(category_expenditures_dict.items()),
            columns=['Category', 'Total Amount']
        )
        plt.figure(figsize=(6, 6))
        sns.heatmap(
            df.set_index('Category'),
            annot=True,
            fmt=".2f",
            cmap="YlGnBu",
            linewidths=0.5,
            cbar_kws={'label': 'Total Amount'},
        )
        plt.title("Expenditure Heatmap by Category", fontsize=16, fontweight="bold")
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        heatmap_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

    # Waterfall Chart preparation
    waterfall_base64 = None
    if float(total_initial_balance) > 0:
        categories = list(category_expenditures_dict.keys()) + ['Remaining Balance']
        values = list(category_expenditures_dict.values()) + [remaining_balance]

        # Prepare Waterfall Data
        data = pd.DataFrame({
            'Category': categories,
            'Values': values,
        })
        data['Cumulative'] = data['Values'].cumsum()

        # Waterfall Chart Plot
        plt.figure(figsize=(8, 6))
        plt.bar(data['Category'], data['Values'], color=(data['Values'] > 0).map({True: 'green', False: 'red'}))
        plt.plot(data['Category'], data['Cumulative'], marker='o', color='blue', label='Cumulative')
        plt.title("Waterfall Chart of Expenditures", fontsize=16, fontweight="bold")
        plt.ylabel("Amount (TZS)")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        waterfall_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

    return heatmap_base64, waterfall_base64, total_initial_balance, category_expenditures_dict, remaining_balance, trend_description, None

from decimal import Decimal
from django.db.models import Sum
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from apps.finance.models import Receipt, StudentUniform
from apps.corecode.models import AcademicSession

def generate_profit_pie_chart():
    """
    Generates a pie chart showing the percentage contributions of income sources to the school's profit.
    Returns:
        - Pie chart as a base64 encoded string.
        - Error message if applicable.
    """
    # Get the current session
    current_session = AcademicSession.objects.filter(current=True).first()

    if not current_session:
        return None, "No current academic session available."

    # Total amount from receipts
    total_receipts = (
        Receipt.objects.filter(invoice__session=current_session)
        .aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
    )

    # Total amount from uniforms
    total_uniforms = (
        StudentUniform.objects.filter(session=current_session)
        .aggregate(total=Sum('amount'))['total'] or Decimal('0')
    )

    # Overall total
    overall_total = total_receipts + total_uniforms

    if overall_total == 0:
        return None, "No income data available for the current session."

    # Calculate percentages
    receipt_percentage = (total_receipts / overall_total) * 100 if overall_total > 0 else 0
    uniform_percentage = (total_uniforms / overall_total) * 100 if overall_total > 0 else 0

    # Generate Pie Chart
    labels = ['Receipts', 'Uniform Sales']
    percentages = [receipt_percentage, uniform_percentage]
    colors = ['#007bff', '#ffc107']

    plt.figure(figsize=(6, 6))
    plt.pie(
        percentages,
        labels=labels,
        autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
        colors=colors,
        startangle=140
    )
    plt.title("Profit Distribution by Source", fontsize=14, fontweight='bold')
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    pie_chart_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    return pie_chart_base64, None


from django.db.models import Sum
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from apps.finance.models import SalaryInvoice
from expenditures.models import ExpenditureInvoice
from apps.corecode.models import AcademicSession


def draw_expenses_analysis():
    """
    Analyzes the school expenses by calculating total expenditure on salaries and other expenses.
    Draws a pie chart for their distribution.
    Returns:
        - Pie chart as a base64 string.
        - Total salary expenses.
        - Total other expenses.
        - Overall total expenses.
        - Comments/Advice/Explanation.
    """
    # Get the current academic session
    current_session = AcademicSession.objects.filter(current=True).first()

    if not current_session:
        return None, 0, 0, 0, "No active session available for analysis."

    # Total salary expenses for the current session
    total_salaries = (
        SalaryInvoice.objects.filter(session=current_session)
        .aggregate(total=Sum('total_given_salary'))['total']
        or 0
    )

    # Total other expenses (ExpenditureInvoice) for the current session
    total_expenditures = (
        ExpenditureInvoice.objects.filter(session=current_session)
        .aggregate(total=Sum('initial_balance'))['total']
        or 0
    )

    # Overall total expenses
    overall_total = total_salaries + total_expenditures

    # Calculate percentages
    data = {
        'Salaries': total_salaries,
        'Expenditures': total_expenditures,
    }
    percentages = {k: (v / overall_total * 100 if overall_total > 0 else 0) for k, v in data.items()}

    # Generate the pie chart
    labels = list(data.keys())
    sizes = list(percentages.values())
    colors = ['#FF6384', '#36A2EB']  # Distinct colors for the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        textprops={'fontsize': 12},
    )
    plt.title(f"Expenses Distribution for {current_session.name}", fontsize=14, fontweight="bold")
    plt.tight_layout()

    # Convert chart to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    pie_chart = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Descriptive comments/advice
    if total_salaries > total_expenditures:
        comments = (
            f"Salaries constitute the majority of expenses in the {current_session.name} session. "
            "Ensure salary expenses are sustainable, and consider strategies to optimize other expenditures."
        )
    elif total_expenditures > total_salaries:
        comments = (
            f"Expenditures other than salaries are the highest in the {current_session.name} session. "
            "Review spending categories for potential cost-cutting opportunities without compromising operational efficiency."
        )
    else:
        comments = (
            f"Salaries and other expenditures are balanced in the {current_session.name} session, "
            "indicating efficient expense management. Continue monitoring to maintain financial stability."
        )

    return pie_chart, total_salaries, total_expenditures, overall_total, comments

import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from django.db.models import Sum
from apps.finance.models import Receipt, StudentUniform, SalaryInvoice
from expenditures.models import ExpenditureInvoice
from apps.corecode.models import AcademicSession

def draw_linear_regression_graph():
    """
    Draws a linear regression graph for the school's balance trends.
    Returns:
        - Linear regression graph (base64 encoded).
        - Historical balance data.
        - Predicted profit for the next session.
        - Predicted expenses for the next session.
        - Predicted balance for the next session.
        - Regression comments and advice.
    """
    from apps.finance.models import Receipt, StudentUniform, SalaryInvoice
    from expenditures.models import ExpenditureInvoice
    from apps.corecode.models import AcademicSession
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64
    import numpy as np
    import pandas as pd

    # Retrieve all sessions
    sessions = AcademicSession.objects.all().order_by('id')

    if not sessions.exists():
        return None, [], 0, 0, 0, "No session data available for analysis."

    balance_data = []  # Store (session_name, balance) for each session

    for session in sessions:
        # Calculate total income for the session
        total_income_receipts = (
            Receipt.objects.filter(invoice__session=session).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        )
        total_income_uniforms = (
            StudentUniform.objects.filter(session=session).aggregate(Sum('amount'))['amount__sum'] or 0
        )
        total_income = float(total_income_receipts) + float(total_income_uniforms)

        # Calculate total expenses for the session
        total_expenses_salaries = (
            SalaryInvoice.objects.filter(session=session).aggregate(Sum('total_given_salary'))['total_given_salary__sum'] or 0
        )
        total_expenses_invoices = (
            ExpenditureInvoice.objects.filter(session=session).aggregate(Sum('initial_balance'))['initial_balance__sum'] or 0
        )
        total_expenses = float(total_expenses_salaries) + float(total_expenses_invoices)

        # Calculate balance
        balance = total_income - total_expenses

        # Add data only if there is actual profit or expenses data
        if total_income > 0 or total_expenses > 0:
            balance_data.append((session.name, balance, total_income, total_expenses))

    if not balance_data:
        return None, [], 0, 0, 0, "No data available for sessions with recorded transactions."

    # Handle single-session case
    if len(balance_data) == 1:
        session_name, balance, total_income, total_expenses = balance_data[0]
        predicted_profit = total_income
        predicted_expenses = total_expenses
        predicted_balance = balance

        # Plot graph for single session
        plt.figure(figsize=(8, 5))
        plt.scatter([session_name], [balance], color='blue', label='Actual Balance', zorder=5)
        plt.axhline(y=balance, color='red', linestyle='--', label='Flat Trend (slope=0)', zorder=4)
        plt.title('Balance Trends Across Sessions', fontsize=14, fontweight='bold')
        plt.xlabel('Session')
        plt.ylabel('Balance (TZS)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        # Convert graph to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        regression_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

        regression_comments = (
            f"Only one session of data available ({session_name}). "
            f"The current balance is TZS {balance:,.2f}, with a total profit of TZS {predicted_profit:,.2f} "
            f"and total expenses of TZS {predicted_expenses:,.2f}. The trend is flat (slope = 0)."
        )
        return regression_graph, balance_data, predicted_profit, predicted_expenses, predicted_balance, regression_comments

    # Prepare data for regression
    df = pd.DataFrame(balance_data, columns=['Session', 'Balance', 'Profit', 'Expenses'])
    df['Session_Number'] = range(1, len(df) + 1)

    # Linear regression calculation
    x = df['Session_Number']
    y = df['Balance']
    coefficients = np.polyfit(x, y, 1)
    regression_line = np.poly1d(coefficients)

    # Predict values for the next session
    next_session_number = len(df) + 1
    predicted_balance = regression_line(next_session_number)
    predicted_profit = df['Profit'].iloc[-1]  # Use profit from the last session
    predicted_expenses = df['Expenses'].iloc[-1]  # Use expenses from the last session

    # Plot the regression graph
    plt.figure(figsize=(12, 6))
    plt.scatter(df['Session'], df['Balance'], color='blue', label='Actual Balances', zorder=5)
    plt.plot(df['Session'], regression_line(df['Session_Number']), color='red', linestyle='--', label='Trend Line', zorder=4)
    plt.axhline(0, color='gray', linewidth=1, linestyle='--', zorder=1)
    plt.title('Balance Trends Across Sessions', fontsize=16, fontweight='bold')
    plt.xlabel('Session')
    plt.ylabel('Balance (TZS)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Convert graph to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    regression_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()

    # Analyze slope for advice
    slope = coefficients[0]
    if slope > 0:
        regression_comments = (
            f"The balance trend shows a positive slope ({slope:.2f}). The school is improving its financial health. "
            "Continue optimizing income and managing expenses for sustainable growth."
        )
    elif slope < 0:
        regression_comments = (
            f"The balance trend shows a negative slope ({slope:.2f}). Immediate action is needed to reverse this trend. "
            "Consider reducing unnecessary expenses and exploring additional income streams."
        )
    else:
        regression_comments = (
            f"The balance trend shows no slope ({slope:.2f}). The school's financial position is stable. "
            "Maintain this stability while exploring opportunities for improvement."
        )

    return regression_graph, balance_data, predicted_profit, predicted_expenses, predicted_balance, regression_comments
