import hashlib
import warnings

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import migrations, models, transaction

from search.private_media_cleanup import (
    cleanup_pending_public_grave_images,
    record_public_grave_image_for_deletion,
)
from search.storage import PrivateGraveImageStorage


def _digest(storage, name):
    digest = hashlib.sha256()
    with storage.open(name, 'rb') as image_file:
        for chunk in image_file.chunks():
            digest.update(chunk)
    return digest.digest()


def _copy_shared_garden_image(apps, public_storage, source_name):
    garden_model = apps.get_model('procurement', 'GardenDetail')
    gardens = garden_model.objects.filter(Lot_Image=source_name)
    if not gardens.exists():
        return

    filename = source_name.rsplit('/', 1)[-1]
    garden_name = f'GardenImages/{filename}'
    with public_storage.open(source_name, 'rb') as source_file:
        garden_name = public_storage.save(garden_name, source_file)

    if _digest(public_storage, source_name) != _digest(public_storage, garden_name):
        raise IOError('Shared garden image copy verification failed.')

    gardens.update(Lot_Image=garden_name)


def _delete_after_commit(storage, name):
    transaction.on_commit(lambda: storage.delete(name))


def _move_grave_images(apps, source_storage, destination_storage, preserve_public_garden_images=False):
    deceased_model = apps.get_model('search', 'DeceasedInformation')
    missing_files = 0

    image_names = (
        deceased_model.objects
        .filter(graveimage__isnull=False)
        .exclude(graveimage='')
        .values_list('graveimage', flat=True)
        .distinct()
    )
    for source_name in image_names.iterator():
        source_exists = source_storage.exists(source_name)
        destination_exists = destination_storage.exists(source_name)

        if not source_exists:
            if destination_exists:
                raise RuntimeError(
                    f'Cannot verify private grave image contents for missing source {source_name!r}.'
                )
            missing_files += 1
            continue

        if preserve_public_garden_images:
            _copy_shared_garden_image(apps, source_storage, source_name)

        if destination_exists and _digest(source_storage, source_name) == _digest(destination_storage, source_name):
            if preserve_public_garden_images:
                record_public_grave_image_for_deletion(source_name)
                transaction.on_commit(cleanup_pending_public_grave_images)
            else:
                _delete_after_commit(source_storage, source_name)
            continue

        with source_storage.open(source_name, 'rb') as source_file:
            destination_name = destination_storage.save(source_name, source_file)
        if _digest(source_storage, source_name) != _digest(destination_storage, destination_name):
            raise IOError('Private grave image copy verification failed.')
        if destination_name != source_name:
            deceased_model.objects.filter(graveimage=source_name).update(graveimage=destination_name)
        if preserve_public_garden_images:
            record_public_grave_image_for_deletion(source_name)
            transaction.on_commit(cleanup_pending_public_grave_images)
        else:
            _delete_after_commit(source_storage, source_name)

    if missing_files:
        warnings.warn(
            f'{missing_files} grave image references had no file in either storage location; '
            'database references were preserved.',
            RuntimeWarning,
        )


def move_to_private_storage(apps, schema_editor):
    source = FileSystemStorage(location=settings.MEDIA_ROOT)
    destination = PrivateGraveImageStorage()
    _move_grave_images(apps, source, destination, preserve_public_garden_images=True)


def restore_to_public_storage(apps, schema_editor):
    source = PrivateGraveImageStorage()
    destination = FileSystemStorage(location=settings.MEDIA_ROOT)
    _move_grave_images(apps, source, destination)


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0010_delete_lotname_deceasedinformation_date_created_and_more'),
        ('procurement', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(move_to_private_storage, restore_to_public_storage),
        migrations.AlterField(
            model_name='deceasedinformation',
            name='graveimage',
            field=models.ImageField(
                blank=True,
                null=True,
                storage=PrivateGraveImageStorage(),
                upload_to='Images/',
            ),
        ),
    ]
