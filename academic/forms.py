from django import forms
from apps.corecode.models import StudentClass, AcademicSession, AcademicTerm, ExamType, Subject
from apps.result.models import Result, StudentInfos
from .models import AcademicAnswer

class ClassSelectionForm(forms.Form):
    class_choices = forms.ModelChoiceField(queryset=StudentClass.objects.all(), widget=forms.RadioSelect)

class ResultEntryForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['test_score', 'exam_score']
        widgets = {
            'test_score': forms.NumberInput(attrs={'class': 'form-control small-input', 'step': '0.01'}),
            'exam_score': forms.NumberInput(attrs={'class': 'form-control small-input', 'step': '0.01'}),
        }

class SessionTermExamSubjectForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; max-width: 600px;'})
    )
    term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; max-width: 600px;'})
    )
    exam = forms.ModelChoiceField(
        queryset=ExamType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'style': 'width: 100%; max-width: 600px;'})
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'subjects'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values if current session, term, or exam exist
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = ExamType.objects.filter(current=True).first()
        
        if current_session:
            self.fields['session'].initial = current_session
        if current_term:
            self.fields['term'].initial = current_term
        if current_exam:
            self.fields['exam'].initial = current_exam

        # If there are no entries, set to None (or handle as needed)
        if not self.fields['session'].queryset.exists():
            self.fields['session'].queryset = AcademicSession.objects.none()
        if not self.fields['term'].queryset.exists():
            self.fields['term'].queryset = AcademicTerm.objects.none()
        if not self.fields['exam'].queryset.exists():
            self.fields['exam'].queryset = ExamType.objects.none()

class DateInput(forms.DateInput):
    input_type = 'date'

class StudentInfosForm(forms.ModelForm):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.none(), required=False)
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.none(), required=False)
    exam = forms.ModelChoiceField(queryset=ExamType.objects.none(), required=False)
    date_of_closing = forms.DateField(widget=DateInput(attrs={'class': 'datepicker'}))
    date_of_opening = forms.DateField(widget=DateInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = StudentInfos
        fields = ['session', 'term', 'exam', 'disprine', 'sports', 'care_of_property', 'collaborations', 'date_of_closing', 'date_of_opening', 'teacher_comments', 'head_comments']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session'].queryset = AcademicSession.objects.all()
        self.fields['term'].queryset = AcademicTerm.objects.all()
        self.fields['exam'].queryset = ExamType.objects.all()
        
        current_session = AcademicSession.objects.filter(current=True).first()
        current_term = AcademicTerm.objects.filter(current=True).first()
        current_exam = ExamType.objects.filter(current=True).first()

        self.fields['session'].initial = current_session if current_session else None
        self.fields['term'].initial = current_term if current_term else None
        self.fields['exam'].initial = current_exam if current_exam else None

class AcademicAnswersForm(forms.ModelForm):
    class Meta:
        model = StudentInfos
        fields = ['academic_answers']
        widgets = {
            'academic_answers': forms.Textarea(attrs={'rows': 4, 'cols': 30, 'class': 'form-control'}),
        }


from django import forms
from .models import AcademicAnswer

class AcademicAnswerForm(forms.ModelForm):
    class Meta:
        model = AcademicAnswer
        fields = ['answer', 'audio_answer']  # Include the audio field
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
        }

    audio_answer = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*'
        }),
        label="Upload an audio file (optional)"
    )
