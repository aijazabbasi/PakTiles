# Generated by Django 5.0.10 on 2024-12-16 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SanitaryItem',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('article_number', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=200)),
                ('brand', models.CharField(max_length=100)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('tile_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(default=None, max_length=255)),
                ('article_number', models.CharField(max_length=255)),
                ('description', models.CharField(default=None, max_length=255)),
                ('tile_size', models.CharField(max_length=100)),
                ('box_size', models.CharField(default=None, max_length=255)),
                ('peiece_per_box', models.CharField(default=None, max_length=255)),
                ('sale_unit', models.CharField(default=None, max_length=255)),
                ('rate', models.DecimalField(decimal_places=2, default=None, max_digits=10)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, default=None, max_digits=10)),
            ],
        ),
    ]