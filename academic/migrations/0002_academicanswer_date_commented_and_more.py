from django.utils import timezone
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicanswer',
            name='date_commented',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='academicanswer',
            name='date_updated_comments',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

