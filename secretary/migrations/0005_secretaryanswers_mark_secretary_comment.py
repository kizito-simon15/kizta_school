# Generated by Django 5.0.4 on 2024-08-20 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretary', '0004_alter_secretaryanswers_answer'),
    ]

    operations = [
        migrations.AddField(
            model_name='secretaryanswers',
            name='mark_secretary_comment',
            field=models.BooleanField(default=False),
        ),
    ]
