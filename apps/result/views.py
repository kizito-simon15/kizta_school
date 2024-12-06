from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DetailView, ListView, View
from apps.corecode.models import AcademicSession, AcademicTerm,ExamType,SiteConfig, StudentClass, Subject
from apps.students.models import Student
from collections import defaultdict
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import StudentInfos
from apps.students.models import Student
from .forms import StudentInfosForm
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, ExamType
from .models import Result, StudentInfos
from django.views.generic.base import TemplateView
from django.db.models import Sum, Avg, Count
from django.forms import formset_factory, modelformset_factory
from django.db.models import Q
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from decimal import Decimal
from .forms import ClassSelectionForm, SessionTermExamSubjectForm, ResultEntryForm
from academic.forms import AcademicAnswersForm
from accounts.forms import ProfilePictureForm
from django.db.models import Prefetch
from academic.models import AcademicAnswer
from academic.forms import AcademicAnswerForm
from parents.models import ParentComments


logger = logging.getLogger(__name__)

@login_required
@permission_required('result.add_result', raise_exception=True)
def create_result(request):
    # Fetch only active students who have not completed school
    students = Student.objects.filter(current_status="active", completed=False)

    # Logic to determine the current session
    current_session = AcademicSession.objects.filter(current=True).first()
    if current_session is None:
        # Handle the case where no session is active for the current date
        # Perhaps set a default session or display an error message
        pass

    # Logic to determine the current term
    current_term = AcademicTerm.objects.filter(current=True).first()
    if current_term is None:
        # Handle the case where no term is active for the current date
        # Perhaps set a default term or display an error message
        pass

    current_exam = ExamType.objects.filter(current=True).first()
    if current_exam is None:
        # Handle the case where no exam type is active
        # Perhaps set a default exam type or display an error message
        pass

    # Set current_session and current_term in the session
    request.session['current_session'] = current_session.id if current_session else None
    request.session['current_term'] = current_term.id if current_term else None
    request.session['current_exam'] = current_exam.id if current_exam else None

    # Group students by class
    students_by_class = {}
    for student in students:
        class_key = student.current_class
        if class_key not in students_by_class:
            students_by_class[class_key] = []
        students_by_class[class_key].append(student)

    if request.method == "POST":
        # after visiting the second page
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                exam = form.cleaned_data["exam"]
                students = request.POST.get("students")
                if students:  # Check if students are selected
                    results = []
                    for student in students.split(","):
                        stu = Student.objects.get(pk=student)
                        if stu.current_class:
                            for subject in subjects:
                                check = Result.objects.filter(
                                    session=session,
                                    term=term,
                                    exam=exam,
                                    current_class=stu.current_class,
                                    subject=subject,
                                    student=stu,
                                ).first()
                                if not check:
                                    results.append(
                                        Result(
                                            session=session,
                                            term=term,
                                            exam=exam,
                                            current_class=stu.current_class,
                                            subject=subject,
                                            student=stu,
                                        )
                                    )

                    Result.objects.bulk_create(results)
                    # Store selected students in session
                    request.session['selected_students'] = students
                    # Store selected student's name in session
                    selected_student_names = ', '.join([f"{Student.objects.get(pk=student_id).firstname} {Student.objects.get(pk=student_id).middle_name} {Student.objects.get(pk=student_id).surname}" for student_id in students.split(",")])
                    request.session['selected_student_name'] = selected_student_names
                    # Redirect to edit-results
                    return redirect("edit-results")
                else:
                    messages.warning(request, "You didn't select any student.")
                    # Render the customized template
                    return render(request, "result/create_result.html", {"students": students, "students_by_class": students_by_class})

        # after choosing students
        id_list = request.POST.getlist("students")
        if id_list:
            # Store selected students in session
            request.session['selected_students'] = id_list
            form = CreateResults(
                initial={
                    "session": request.session.get('current_session'),
                    "term": request.session.get('current_term'),
                    "exam": request.session.get('current_exam'),
                }
            )
            studentlist = ",".join(id_list)
            return render(
                request,
                "result/create_result_page2.html",  # Render create_results_part2.html template
                {"students": studentlist, "form": form, "count": len(id_list), "students_by_class": students_by_class},
            )
        else:
            messages.warning(request, "You didn't select any student.")

    # Render the customized template
    return render(request, "result/create_result.html", {"students": students, "students_by_class": students_by_class})

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DetailView, ListView, View
from apps.corecode.models import AcademicSession, AcademicTerm,ExamType,SiteConfig, StudentClass, Subject
from apps.students.models import Student
from collections import defaultdict
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import StudentInfos
from apps.students.models import Student
from .forms import StudentInfosForm
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, ExamType
from .forms import CreateResults, EditResults, ViewResultsForm, ViewResultsFormSet, StudentInfosForm
from .models import Result, StudentInfos
from django.views.generic.base import TemplateView
from django.db.models import Sum, Avg, Count
from django.forms import formset_factory, modelformset_factory
from django.db.models import Q
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import logging
from decimal import Decimal
from django.db.models import Prefetch
from academic.models import AcademicAnswer
from academic.forms import AcademicAnswerForm
from parents.models import ParentComments
from apps.corecode.models import Signature

@login_required
@permission_required('result.change_result', raise_exception=True)
def edit_results(request):
    logger.debug("Entering the edit_results view")
    student_classes = StudentClass.objects.all()
    subjects = Subject.objects.all()
    logger.debug("Fetched student classes and subjects: %s, %s", student_classes, subjects)

    if request.method == "POST":
        logger.debug("Handling POST request")
        formset = EditResults(request.POST)

        if formset.is_valid():
            logger.debug("Formset is valid. Processing forms...")
            for form in formset:
                if form.cleaned_data.get('DELETE', False):
                    logger.debug("Processing deletion for form: %s", form.instance)
                    instance = form.instance
                    if instance.pk:
                        instance.delete()
                        logger.debug("Deleted instance: %s", instance)
                else:
                    instance = form.save(commit=False)
                    logger.debug("Saving instance: %s", instance)
                    instance.calculate_result()  # Apply custom logic
                    instance.save()
            messages.success(request, "Results successfully updated.")
            return redirect("edit-results")
        else:
            logger.error("Formset is invalid. Errors: %s", formset.errors)
            for i, form in enumerate(formset):
                if form.errors:
                    logger.error("Form %d errors: %s", i, form.errors)
            messages.error(request, "There was an error updating the results. Please fix the errors and try again.")
    else:
        logger.debug("Handling GET request")
        class_select = request.GET.get('class_select')
        subject_select = request.GET.get('subject_select')
        student_name = request.GET.get('student_name')

        logger.debug("Filters: class_select=%s, subject_select=%s, student_name=%s", class_select, subject_select, student_name)

        results = Result.objects.filter(
            session=request.current_session,
            term=request.current_term,
            exam=request.current_exam
        )

        if class_select:
            results = results.filter(current_class_id=class_select)
            logger.debug("Filtered results by class_select: %s", results)

        if subject_select:
            results = results.filter(subject_id=subject_select)
            logger.debug("Filtered results by subject_select: %s", results)

        if student_name:
            results = results.filter(
                Q(student__firstname__icontains=student_name) |
                Q(student__middle_name__icontains=student_name) |
                Q(student__surname__icontains=student_name)
            )
            logger.debug("Filtered results by student_name: %s", results)

        formset = EditResults(queryset=results)
        logger.debug("Created formset with queryset: %s", results)

    logger.debug("Rendering edit_results template with context")
    return render(request, "result/edit_results.html", {
        "formset": formset,
        "student_classes": student_classes,
        "subjects": subjects
    })

@login_required
def edit_now_results(request):
    if request.method == 'POST':
        result_ids = request.POST.getlist('result_ids')
        for result_id in result_ids:
            result = get_object_or_404(Result, id=result_id)
            form = ResultEntryForm(request.POST, instance=result, prefix=f'result_{result_id}')
            if form.is_valid():
                form.save()
        messages.success(request, 'Results updated successfully.')
        return redirect('edit-results')

    else:
        results = Result.objects.all()
        result_forms = [(result, ResultEntryForm(instance=result, prefix=f'result_{result.id}')) for result in results]

    current_session = AcademicSession.objects.filter(current=True).first()
    current_term = AcademicTerm.objects.filter(current=True).first()
    current_exam_type = ExamType.objects.filter(current=True).first()

    context = {
        'result_forms': result_forms,
        'sessions': AcademicSession.objects.all(),
        'terms': AcademicTerm.objects.all(),
        'exam_types': ExamType.objects.all(),
        'student_classes': StudentClass.objects.all(),
        'subjects': Subject.objects.all(),
        'current_session': current_session,
        'current_term': current_term,
        'current_exam_type': current_exam_type,
    }
    return render(request, 'result/edit_now_results.html', context)

@login_required
@permission_required('result.delete_page', raise_exception=True)
@login_required
def delete_page_results(request):
    if request.method == "POST":
        class_select = request.POST.get('class_select')
        subject_select = request.POST.get('subject_select')
        student_name = request.POST.get('student_name')

        results = Result.objects.filter(session=request.current_session, term=request.current_term, exam=request.current_exam)

        if class_select:
            results = results.filter(current_class_id=class_select)

        if subject_select:
            results = results.filter(subject_id=subject_select)

        if student_name:
            results = results.filter(
                Q(student__firstname__icontains=student_name) |
                Q(student__surname__icontains=student_name) |
                Q(student__middle_name__icontains=student_name)
            )

        count, _ = results.delete()
        messages.success(request, f"Deleted {count} results successfully.")
        return redirect("edit-results")
    else:
        class_select = request.GET.get('class_select')
        subject_select = request.GET.get('subject_select')
        student_name = request.GET.get('student_name')

        context = {
            'class_select': class_select,
            'subject_select': subject_select,
            'student_name': student_name,
        }
        return render(request, 'result/confirm_delete_page_results.html', context)

class StudentResultsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'result/student_results.html'
    permission_required = "result.view_result"

    def get(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)
        form = StudentInfosForm(instance=student.studentinfos_set.filter(
            session=AcademicSession.objects.filter(current=True).first(),
            term=AcademicTerm.objects.filter(current=True).first(),
            exam=ExamType.objects.filter(current=True).first(),
        ).last())  # Retrieve the last saved form instance for the current session, term, and exam
        session = AcademicSession.objects.filter(current=True).first()
        term = AcademicTerm.objects.filter(current=True).first()
        exam_type = ExamType.objects.filter(current=True).first()
        student_class = student.current_class

        return render(request, self.template_name, {
            'form': form,
            'session': session,
            'term': term,
            'exam_type': exam_type,
            'student_class': student_class,
            'student': student,
        })

    def post(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)
        session = AcademicSession.objects.filter(current=True).first()
        term = AcademicTerm.objects.filter(current=True).first()
        exam_type = ExamType.objects.filter(current=True).first()
        student_class = student.current_class

        form = StudentInfosForm(request.POST)
        if form.is_valid():
            student_info = form.save(commit=False)
            student_info.student = student
            student_info.session = session
            student_info.term = term
            student_info.exam = exam_type
            student_info.save()
            messages.success(request, 'The student information has been saved successfully.')
            return redirect('student-results', student_id=student_id)

        return render(request, self.template_name, {
            'form': form,
            'session': session,
            'term': term,
            'exam_type': exam_type,
            'student_class': student_class,
            'student': student,
        })


from django.db.models import Sum, Avg, Count
from apps.corecode.models import Signature

class FormStatusView(LoginRequiredMixin, View):
    template_name = 'result/form_status.html'

    def calculate_overall_grade(self, overall_average):
        if overall_average >= 41:
            return "A"
        elif 30 <= overall_average < 41:
            return "B"
        elif 25 <= overall_average < 30:
            return "C"
        elif 15 <= overall_average < 25:
            return "D"
        else:
            return "F"

    def calculate_overall_total_marks(self, student):
        subject_count = student.result_set.values('subject').distinct().count()
        return subject_count * 50

    def get_total_active_students(self, class_id, current_session, current_term, current_exam_type):
        """
        Calculate the total number of active students who have not completed school in the given class,
        session, term, and exam.
        """
        return Student.objects.filter(
            result__current_class_id=class_id,
            result__session=current_session,
            result__term=current_term,
            result__exam=current_exam_type,
            current_status="active",
            completed=False
        ).distinct().count()

    def get(self, request, class_id):
        student_class = get_object_or_404(StudentClass, pk=class_id)

        current_session = request.GET.get('session', AcademicSession.objects.filter(current=True).first().id)
        current_term = request.GET.get('term', AcademicTerm.objects.filter(current=True).first().id)
        current_exam_type = request.GET.get('exam', ExamType.objects.filter(current=True).first().id)

        sessions = AcademicSession.objects.all()
        terms = AcademicTerm.objects.all()
        exams = ExamType.objects.all()

        # Calculate the total active students
        total_active_students = self.get_total_active_students(class_id, current_session, current_term, current_exam_type)

        students_with_forms = Student.objects.filter(
            result__current_class=student_class,
            result__session=current_session,
            result__term=current_term,
            result__exam=current_exam_type
        ).distinct()

        query = request.GET.get('q')
        if query:
            students_with_forms = students_with_forms.filter(
                Q(firstname__icontains=query) | Q(middle_name__icontains=query) | Q(surname__icontains=query) | Q(registration_number=query)
            )

        no_forms = not students_with_forms.exists()

        completed_forms_count = 0
        for student_info in students_with_forms:
            last_student_info = student_info.studentinfos_set.last()
            if last_student_info:
                if all([
                    last_student_info.disprine,
                    last_student_info.sports,
                    last_student_info.care_of_property,
                    last_student_info.collaborations,
                    last_student_info.date_of_closing,
                    last_student_info.date_of_opening,
                    last_student_info.teacher_comments,
                    last_student_info.head_comments
                ]):
                    completed_forms_count += 1

        student_results = []
        for student in students_with_forms:
            student_results_queryset = student.result_set.filter(
                current_class=student_class,
                session=current_session,
                term=current_term,
                exam=current_exam_type
            )

            total_average = student_results_queryset.aggregate(Sum('average'))['average__sum']
            overall_average = student_results_queryset.aggregate(Avg('average'))['average__avg']
            overall_grade = self.calculate_overall_grade(overall_average) if overall_average is not None else "No results available"
            overall_total_marks = self.calculate_overall_total_marks(student)

            student_results.append({
                'student': student,
                'total_average': total_average,
                'overall_average': overall_average,
                'overall_grade': overall_grade,
                'overall_total_marks': overall_total_marks,
                'results': student_results_queryset
            })

        # Sort students by overall average in descending order
        sorted_results = sorted(student_results, key=lambda x: x['overall_average'] or 0, reverse=True)

        # Assign positions with tie handling
        current_position = 1
        i = 0

        while i < len(sorted_results):
            tie_group = [sorted_results[i]]
            j = i + 1

            while j < len(sorted_results) and sorted_results[j]['overall_average'] == sorted_results[i]['overall_average']:
                tie_group.append(sorted_results[j])
                j += 1

            # Calculate average position for the tie group
            if len(tie_group) > 1:
                average_position = current_position + 0.5
                for result in tie_group:
                    result['position'] = average_position
            else:
                tie_group[0]['position'] = current_position

            # Move to the next group
            current_position += len(tie_group)
            i = j

        # Retrieve the Headmaster's signature
        headmaster_signature = Signature.objects.filter(name="Headmaster's signature").first()

        return render(request, self.template_name, {
            'student_class': student_class,
            'students_with_forms': students_with_forms,
            'student_results': sorted_results,
            'sessions': sessions,
            'terms': terms,
            'exams': exams,
            'current_session': AcademicSession.objects.get(id=current_session),
            'current_term': AcademicTerm.objects.get(id=current_term),
            'current_exam_type': ExamType.objects.get(id=current_exam_type),
            'completed_forms_count': completed_forms_count,
            'no_forms': no_forms,
            'total_active_students': total_active_students,  # Pass total active students to the template
            'academic_answer_form': AcademicAnswerForm(),
            'headmaster_signature': headmaster_signature,
        })

    def post(self, request, class_id):
        form = AcademicAnswerForm(request.POST)
        if form.is_valid():
            current_session = request.POST.get('session')
            current_term = request.POST.get('term')
            current_exam_type = request.POST.get('exam')
            student_id = request.POST.get('student_id')

            student = get_object_or_404(Student, pk=student_id)
            session = get_object_or_404(AcademicSession, pk=current_session)
            term = get_object_or_404(AcademicTerm, pk=current_term)
            exam = get_object_or_404(ExamType, pk=current_exam_type)

            academic_answer, created = AcademicAnswer.objects.get_or_create(
                session=session,
                term=term,
                exam=exam,
                student=student
            )
            academic_answer.answer = form.cleaned_data['answer']
            academic_answer.save()

            messages.success(request, 'Academic answer saved successfully.')
            return redirect('form_status', class_id=class_id)

        messages.error(request, 'There was an error saving the academic answer.')
        return redirect('form_status', class_id=class_id)

class ClassResultsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'result/class_results.html'
    permission_required = "result.view_result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        selected_class = StudentClass.objects.get(pk=class_id)
        
        session_id = self.request.GET.get('session', None)
        term_id = self.request.GET.get('term', None)
        exam_id = self.request.GET.get('exam', None)
        
        if session_id:
            session = AcademicSession.objects.get(id=session_id)
        else:
            session = AcademicSession.objects.get(current=True)
        
        if term_id:
            term = AcademicTerm.objects.get(id=term_id)
        else:
            term = AcademicTerm.objects.get(current=True)
        
        if exam_id:
            exam = ExamType.objects.get(id=exam_id)
        else:
            exam = ExamType.objects.get(current=True)

        context['class_id'] = class_id
        context['selected_class'] = selected_class
        context['sessions'] = AcademicSession.objects.all()
        context['terms'] = AcademicTerm.objects.all()
        context['exams'] = ExamType.objects.all()
        context['current_session'] = session
        context['current_term'] = term
        context['current_exam'] = exam

        # Retrieve results based on the given class, session, term, and exam
        results = Result.objects.filter(
            current_class=selected_class,
            session=session,
            term=term,
            exam=exam
        ).select_related('student')

        if not results.exists():
            context['no_results'] = True
            return context

        context['no_results'] = False

        data = []
        subjects = set()

        # Group results by student
        student_results_map = {}
        for result in results:
            if result.student not in student_results_map:
                student_results_map[result.student] = []
            student_results_map[result.student].append(result)

        for student, student_results in student_results_map.items():
            student_data = {
                'student': student,
                'student_class': selected_class,  # Use the class from the Result model
                'subjects': {}
            }

            # Calculate total marks and overall average
            total_marks = sum(res.average for res in student_results)
            overall_average = total_marks / len(student_results) if student_results else 0
            overall_status = "PASS" if overall_average >= 25 else "FAIL"

            student_data['total'] = total_marks
            student_data['overall_average'] = overall_average
            student_data['overall_status'] = overall_status

            for result in student_results:
                subjects.add(result.subject.name)
                student_data['subjects'][result.subject.name] = {
                    'test_score': result.test_score,
                    'exam_score': result.exam_score,
                    'average': result.average
                }

            data.append(student_data)

        # Sort students by overall average in descending order
        sorted_data = sorted(data, key=lambda x: x['overall_average'], reverse=True)

        # Assign positions with tie handling
        current_position = 1
        i = 0

        while i < len(sorted_data):
            tie_group = [sorted_data[i]]
            j = i + 1

            while j < len(sorted_data) and sorted_data[j]['overall_average'] == sorted_data[i]['overall_average']:
                tie_group.append(sorted_data[j])
                j += 1

            # Calculate average position for the tie group
            if len(tie_group) > 1:
                average_position = current_position + 0.5
                for student_data in tie_group:
                    student_data['position'] = average_position
            else:
                tie_group[0]['position'] = current_position

            # Move to the next group
            current_position += len(tie_group)
            i = j

        context['data'] = sorted_data
        context['subjects'] = sorted(subjects)

        # Calculate subject averages, grades, and GPAs for the given class
        subject_data = []
        for subject_name in subjects:
            subject = Subject.objects.get(name=subject_name)
            subject_average = self.calculate_subject_average(selected_class, subject, session, term, exam)
            subject_grade = self.calculate_subject_grade(subject_average)
            subject_gpa = self.calculate_subject_gpa(selected_class, subject, session, term, exam)
            subject_data.append({
                'subject': subject_name,
                'average': subject_average,
                'grade': subject_grade,
                'gpa': subject_gpa
            })
        context['subject_data'] = sorted(subject_data, key=lambda x: x['average'], reverse=True)

        return context

    def calculate_subject_average(self, student_class, subject, session, term, exam):
        results = Result.objects.filter(
            current_class=student_class,
            subject=subject,
            session=session,
            term=term,
            exam=exam
        )

        total_average = results.aggregate(total_average=Sum('average'))['total_average'] or 0
        count = results.count()
        if count == 0:
            return 0.00
        else:
            return round(total_average / count, 2)

    def calculate_subject_grade(self, subject_average):
        if subject_average > 41:
            return "A"
        elif 31 <= subject_average < 41:
            return "B"
        elif 25 <= subject_average < 31:
            return "C"
        elif 15 <= subject_average < 25:
            return "D"
        else:
            return "F"

    def calculate_subject_gpa(self, student_class, subject, session, term, exam):
        results = Result.objects.filter(
            current_class=student_class,
            subject=subject,
            session=session,
            term=term,
            exam=exam
        )

        count = results.count()
        if count == 0:
            return 0.00

        total_average = results.aggregate(total_average=Sum('average'))['total_average'] or Decimal(0)
        subject_average = total_average / count
        max_score = Decimal(50)
        gpa = (subject_average / max_score) * Decimal(4.0)

        return round(gpa, 2)

# this display the list of the classes and the user will select the class whose results is going to see in the ClassResultsView
class ClassListView(View):
    def get(self, request):
        # Retrieve all classes
        classes = StudentClass.objects.all()
        context = {
            'classes': classes
        }
        return render(request, 'result/class_list.html', context)

    def post(self, request):
        # Get the selected class ID from the POST request
        class_id = request.POST.get('class_id')
        if class_id:
            # Redirect to ClassResultsView with the selected class ID
            return redirect('class-results', class_id=class_id)
        else:
            # If no class is selected, redirect bfrom django.core.validators import MinValueValidator, MaxValueValidator
            # If no class is selected, redirect back to the class list page
            return redirect('class-list')

from itertools import groupby
from collections import defaultdict

class SingleClassResultsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'result/single_class_results.html'
    permission_required = "result.view_result"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_id = self.kwargs.get('class_id')
        selected_class = StudentClass.objects.get(pk=class_id)

        session_id = self.request.GET.get('session', None)
        term_id = self.request.GET.get('term', None)
        exam_id = self.request.GET.get('exam', None)

        if session_id:
            session = AcademicSession.objects.get(id=session_id)
        else:
            session = AcademicSession.objects.get(current=True)

        if term_id:
            term = AcademicTerm.objects.get(id=term_id)
        else:
            term = AcademicTerm.objects.get(current=True)

        if exam_id:
            exam = ExamType.objects.get(id=exam_id)
        else:
            exam = ExamType.objects.get(current=True)

        context['class_id'] = class_id
        context['selected_class'] = selected_class
        context['sessions'] = AcademicSession.objects.all()
        context['terms'] = AcademicTerm.objects.all()
        context['exams'] = ExamType.objects.all()
        context['current_session'] = session
        context['current_term'] = term
        context['current_exam'] = exam

        # Retrieve results based on the given class, session, term, and exam
        results = Result.objects.filter(
            current_class=selected_class,
            session=session,
            term=term,
            exam=exam
        ).select_related('student')

        if not results.exists():
            context['no_results'] = True
            return context

        context['no_results'] = False

        data = []
        subjects = set()

        # Group results by student
        student_results_map = {}
        for result in results:
            if result.student not in student_results_map:
                student_results_map[result.student] = []
            student_results_map[result.student].append(result)

        for student, student_results in student_results_map.items():
            student_data = {
                'student': student,
                'student_class': selected_class,  # Use the class from the Result model
                'subjects': {}
            }

            # Calculate total marks and overall average
            total_marks = sum(res.average for res in student_results)
            overall_average = total_marks / len(student_results) if student_results else 0
            overall_status = "PASS" if overall_average >= 25 else "FAIL"

            student_data['total'] = total_marks
            student_data['overall_average'] = overall_average
            student_data['overall_status'] = overall_status

            for result in student_results:
                subjects.add(result.subject.name)
                student_data['subjects'][result.subject.name] = {
                    'test_score': result.test_score,
                    'exam_score': result.exam_score,
                    'average': result.average
                }

            data.append(student_data)

        # Sort students by overall average in descending order
        sorted_data = sorted(data, key=lambda x: x['overall_average'], reverse=True)

        # Assign positions with tie handling
        current_position = 1
        i = 0

        while i < len(sorted_data):
            tie_group = [sorted_data[i]]
            j = i + 1

            while j < len(sorted_data) and sorted_data[j]['overall_average'] == sorted_data[i]['overall_average']:
                tie_group.append(sorted_data[j])
                j += 1

            # Calculate average position for the tie group
            if len(tie_group) > 1:
                average_position = current_position + 0.5
                for student_data in tie_group:
                    student_data['position'] = average_position
            else:
                tie_group[0]['position'] = current_position

            # Move to the next group
            current_position += len(tie_group)
            i = j

        context['data'] = sorted_data
        context['subjects'] = sorted(subjects)

        # Calculate subject averages, grades, and GPAs for the given class
        subject_data = []
        for subject_name in subjects:
            subject = Subject.objects.get(name=subject_name)
            subject_average = self.calculate_subject_average(selected_class, subject, session, term, exam)
            subject_grade = self.calculate_subject_grade(subject_average)
            subject_gpa = self.calculate_subject_gpa(selected_class, subject, session, term, exam)
            subject_data.append({
                'subject': subject_name,
                'average': subject_average,
                'grade': subject_grade,
                'gpa': subject_gpa
            })
        context['subject_data'] = sorted(subject_data, key=lambda x: x['average'], reverse=True)

        return context

    def calculate_subject_average(self, student_class, subject, session, term, exam):
        results = Result.objects.filter(
            current_class=student_class,
            subject=subject,
            session=session,
            term=term,
            exam=exam
        )

        total_average = results.aggregate(total_average=Sum('average'))['total_average'] or 0
        count = results.count()
        if count == 0:
            return 0.00
        else:
            return round(total_average / count, 2)

    def calculate_subject_grade(self, subject_average):
        if subject_average > 41:
            return "A"
        elif 31 <= subject_average < 41:
            return "B"
        elif 25 <= subject_average < 31:
            return "C"
        elif 15 <= subject_average < 25:
            return "D"
        else:
            return "F"

    def calculate_subject_gpa(self, student_class, subject, session, term, exam):
        results = Result.objects.filter(
            current_class=student_class,
            subject=subject,
            session=session,
            term=term,
            exam=exam
        )

        count = results.count()
        if count == 0:
            return 0.00

        total_average = results.aggregate(total_average=Sum('average'))['total_average'] or Decimal(0)
        subject_average = total_average / count
        max_score = Decimal(50)
        gpa = (subject_average / max_score) * Decimal(4.0)

        return round(gpa, 2)
    
# this display the list of the classes and the user will select the class whose results is going to see in the ClassResultsView
class SingleClassListView(View):
    def get(self, request):
        # Retrieve all classes
        classes = StudentClass.objects.all()
        context = {
            'classes': classes
        }
        return render(request, 'result/single_class_list.html', context)

    def post(self, request):
        # Get the selected class ID from the POST request
        class_id = request.POST.get('class_id')
        if class_id:
            # Redirect to ClassResultsView with the selected class ID
            return redirect('single-results', class_id=class_id)
        else:
            # If no class is selected, redirect bfrom django.core.validators import MinValueValidator, MaxValueValidator
            # If no class is selected, redirect back to the class list page
            return redirect('single-class')


# In views.py
class SingleStudentResultsView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'result/single_student_results.html'
    permission_required = 'result.view_single_student_results'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_id = kwargs.get('student_id')  # Assuming you pass the student id through URL

        # Retrieve the student
        student = Student.objects.get(pk=student_id)

        # Get the current academic session, term, and exam
        current_session = AcademicSession.objects.get(current=True)
        current_term = AcademicTerm.objects.get(current=True)
        current_exam = ExamType.objects.get(current=True)

        # Retrieve results for the specified student, session, term, and exam
        student_results = Result.objects.filter(
            student_id=student_id,
            session=current_session,
            term=current_term,
            exam=current_exam
        )

        # Pass the student's name and registration number to the template
        context['student_name'] = f"{student.firstname} {student.middle_name} {student.surname}"
        context['registration_number'] = student.registration_number

        # Calculate total marks for each subject
        subjects = {}
        for result in student_results:
            subject_name = result.subject.name
            if subject_name not in subjects:
                subjects[subject_name] = {
                    'test_score': result.test_score or 0,
                    'exam_score': result.exam_score or 0,
                    'average': result.average or 0,
                    'grade': result.calculate_grade(),
                    'status': result.calculate_status(),
                    'comments': result.calculate_comments()  # Calculate comments for each result
                }
            else:
                subjects[subject_name]['test_score'] += result.test_score or 0
                subjects[subject_name]['exam_score'] += result.exam_score or 0
                subjects[subject_name]['average'] += result.average or 0

        # Pass the calculated results to the template
        context['subjects'] = subjects

        # Calculate total marks, total marks of all subjects, overall average, overall grade,
        # position, and total students
        total = sum(result.total for result in student_results)
        total_marks = sum(result.calculate_overall_total_marks() for result in student_results)
        if student_results:
            overall_average = sum(result.overall_average for result in student_results) / len(student_results)
        else:
            overall_average = None  # or any default value you prefer

        if student_results:
            overall_grade = student_results[0].calculate_overall_grade(student)
        else:
            overall_grade = None

        position = Result.calculate_position(overall_average)

        # Add these values to the context
        context.update({
            'total': total,
            'total_marks': total_marks,
            'overall_average': overall_average,
            'overall_grade': overall_grade,
            'position': position,
            'student_id': student_id,  # Pass student_id to the context
        })

        return context

@login_required
def admin_profile(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # Replace 'academic_dashboard' with your actual dashboard URL name
    else:
        form = ProfilePictureForm(instance=request.user)
    return render(request, 'result/admin_profile.html', {'form': form})
