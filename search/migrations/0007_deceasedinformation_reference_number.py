# Generated by Django 4.0.5 on 2022-10-21 17:20

from django.db import migrations, models
import search.models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0006_alter_deceasedinformation_graveimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='deceasedinformation',
            name='reference_number',
            field=models.CharField(default=search.models.randomGenerator, editable=False, max_length=10),
        ),
    ]
