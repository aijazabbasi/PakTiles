# Generated by Django 5.0.10 on 2024-12-17 02:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_remove_order_total_bill_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordersanitarydetails',
            name='sanitary',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='sanitary_details', to='main.sanitaryitem'),
            preserve_default=False,
        ),
    ]
