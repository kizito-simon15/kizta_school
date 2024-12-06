# apps/disprine/migrations/0005_add_default_discipline_issue.py

from django.db import migrations, models
import django.utils.timezone

def create_default_discipline_issue(apps, schema_editor):
    DisciplineIssue = apps.get_model('disprine', 'DisciplineIssue')
    Student = apps.get_model('students', 'Student')
    Action = apps.get_model('disprine', 'Action')

    # Create a default student if one doesn't exist
    default_student, created = Student.objects.get_or_create(
        registration_number='default',
        defaults={
            'firstname': 'Default',
            'surname': 'Student',
            'date_of_birth': django.utils.timezone.now(),
            'date_of_admission': django.utils.timezone.now()
        }
    )

    # Create a default discipline issue
    default_issue = DisciplineIssue.objects.create(
        student=default_student,
        issue_description='Default issue description',
        date_reported=django.utils.timezone.now()
    )

    # Update all existing actions to point to the default discipline issue
    Action.objects.filter(discipline_issue_id=0).update(discipline_issue=default_issue)

class Migration(migrations.Migration):

    dependencies = [
        ('disprine', '0003_action_discipline_issue'),
        ('students', '0001_initial'),  # Ensure this matches your actual initial migration for the students app
    ]

    operations = [
        migrations.RunPython(create_default_discipline_issue),
    ]

