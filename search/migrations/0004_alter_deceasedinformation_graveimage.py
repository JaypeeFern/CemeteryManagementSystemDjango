# Generated by Django 4.0.5 on 2022-09-28 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_alter_deceasedinformation_graveimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deceasedinformation',
            name='graveimage',
            field=models.ImageField(blank=True, null=True, upload_to='Images/'),
        ),
    ]
