# Generated by Django 4.2.7 on 2023-11-06 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_customuser_options_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='phone_no',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
    ]
