# Generated by Django 5.0.4 on 2024-08-17 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secretary', '0002_secretarynotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secretaryanswers',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='secretarynotification',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]