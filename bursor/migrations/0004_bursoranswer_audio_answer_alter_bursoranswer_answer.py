# Generated by Django 5.1.2 on 2024-11-01 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bursor", "0003_bursoranswer_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="bursoranswer",
            name="audio_answer",
            field=models.FileField(
                blank=True, null=True, upload_to="bursor_audio_answers/"
            ),
        ),
        migrations.AlterField(
            model_name="bursoranswer",
            name="answer",
            field=models.TextField(blank=True),
        ),
    ]
