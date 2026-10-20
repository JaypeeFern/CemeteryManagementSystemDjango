from django.conf import settings
from django.db import migrations


def deactivate_unapproved_accounts(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    User.objects.using(schema_editor.connection.alias).filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
    ).update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0001_invalidate_exposed_sessions'),
    ]

    operations = [
        migrations.RunPython(deactivate_unapproved_accounts, migrations.RunPython.noop),
    ]
