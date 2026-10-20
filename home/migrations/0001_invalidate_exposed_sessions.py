from django.db import migrations, models


def invalidate_sessions(apps, schema_editor):
    Session = apps.get_model('sessions', 'Session')
    Session.objects.using(schema_editor.connection.alias).all().delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestThrottleBucket',
            fields=[
                ('bucket_key', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('count', models.PositiveIntegerField(default=1)),
                ('expires_at', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'home_request_throttle_bucket',
            },
        ),
        migrations.RunPython(invalidate_sessions, migrations.RunPython.noop),
    ]
