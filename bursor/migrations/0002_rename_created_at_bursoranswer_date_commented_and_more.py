# Generated by Django 5.0.4 on 2024-08-15 21:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_customuser_profile_picture'),
        ('bursor', '0001_initial'),
        ('corecode', '0001_initial'),
        ('finance', '0010_uniformtype_alter_uniform_uniform_type'),
        ('students', '0009_student_completed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bursoranswer',
            old_name='created_at',
            new_name='date_commented',
        ),
        migrations.RemoveField(
            model_name='bursoranswer',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='bursoranswer',
            name='term',
        ),
        migrations.AddField(
            model_name='bursoranswer',
            name='date_updated_comments',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='bursoranswer',
            name='installment',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='corecode.installment'),
        ),
        migrations.AddField(
            model_name='bursoranswer',
            name='invoice',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='finance.invoice'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bursoranswer',
            name='parent',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='accounts.parentuser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bursoranswer',
            name='satisfied',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bursoranswer',
            name='session',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='corecode.academicsession'),
        ),
        migrations.AlterField(
            model_name='bursoranswer',
            name='student',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='students.student'),
        ),
    ]