# Generated by Django 4.2.7 on 2023-12-10 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('InventoryApp', '0008_iteminventory_invoice_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminventory',
            name='Invoice_no',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_no', to='InventoryApp.invoice'),
        ),
    ]
