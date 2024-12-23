# Generated by Django 4.2.7 on 2024-11-21 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('HostelApp', '0007_useravailabilitycheck'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealhistory',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='mealhistory',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='meal_history_updated', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mealhistory',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
