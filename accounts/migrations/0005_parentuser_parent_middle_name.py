# Generated by Django 5.0.4 on 2024-06-18 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_parentuser_groups_parentuser_user_permissions_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="parentuser",
            name="parent_middle_name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]