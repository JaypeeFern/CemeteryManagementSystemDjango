# Generated by Django 4.0.5 on 2022-10-21 17:22

from django.db import migrations, models
import search.models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_deceasedinformation_reference_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deceasedinformation',
            name='reference_number',
            field=models.CharField(default=search.models.randomGenerator, max_length=10),
        ),
    ]