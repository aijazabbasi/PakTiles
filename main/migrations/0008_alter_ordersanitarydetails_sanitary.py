# Generated by Django 5.0.10 on 2024-12-17 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_ordersanitarydetails_sanitary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordersanitarydetails',
            name='sanitary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sanitaryitem_details', to='main.sanitaryitem'),
        ),
    ]
