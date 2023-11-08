# Generated by Django 4.2.7 on 2023-11-08 06:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MealHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('lunch', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('dinner', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('meal_sum_per_day', models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
