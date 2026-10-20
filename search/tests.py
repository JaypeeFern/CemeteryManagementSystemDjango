import base64
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousFileOperation
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.db import connection
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.db.migrations.executor import MigrationExecutor
from django.http import Http404
from django.test import RequestFactory

from procurement.models import GardenDetail, LotType
from search.models import DeceasedInformation, Location
from search.private_media_cleanup import (
    PENDING_PUBLIC_GRAVE_IMAGE_DELETIONS,
    cleanup_pending_public_grave_images,
    record_public_grave_image_for_deletion,
)
from search.storage import PrivateGraveImageStorage
from search.views import private_grave_image


PNG_IMAGE = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/S9sAAAAASUVORK5CYII='
)


class PrivateGraveImageAccessTests(TestCase):
    def setUp(self):
        self.public_directory = tempfile.TemporaryDirectory()
        self.private_directory = tempfile.TemporaryDirectory()
        settings_override = override_settings(
            MEDIA_ROOT=self.public_directory.name,
            PRIVATE_MEDIA_ROOT=self.private_directory.name,
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.addCleanup(self.public_directory.cleanup)
        self.addCleanup(self.private_directory.cleanup)

        self.location = Location.objects.create(grave_lot_id='01', grave_area='TEST GARDEN')
        self.deceased = DeceasedInformation.objects.create(
            name='Synthetic Record',
            born='1900-01-01',
            died='1980-01-01',
            location=self.location,
        )
        self.deceased.graveimage.save('marker.png', ContentFile(PNG_IMAGE), save=True)
        self.active_user = User.objects.create_user(
            username='approved-user',
            password='a-long-synthetic-password',
            is_active=True,
        )

    def test_anonymous_user_cannot_read_grave_image(self):
        response = self.client.get(
            reverse('PrivateGraveImageForRecord', kwargs={'pk': self.deceased.pk}),
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('Home'), response['Location'])

    def test_active_user_can_read_private_image_with_non_shared_cache_headers(self):
        self.client.force_login(self.active_user)

        response = self.client.get(
            reverse('PrivateGraveImageForRecord', kwargs={'pk': self.deceased.pk}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(b''.join(response.streaming_content), PNG_IMAGE)

    def test_inactive_user_with_a_stale_session_cannot_read_image(self):
        inactive_user = User.objects.create_user(
            username='pending-user',
            password='another-long-synthetic-password',
            is_active=False,
        )
        self.client.force_login(inactive_user)

        response = self.client.get(
            reverse('PrivateGraveImageForRecord', kwargs={'pk': self.deceased.pk}),
        )

        self.assertEqual(response.status_code, 302)

    def test_missing_record_or_file_returns_not_found(self):
        self.client.force_login(self.active_user)

        missing_record = self.client.get(
            reverse('PrivateGraveImageForRecord', kwargs={'pk': self.deceased.pk + 100}),
        )
        self.deceased.graveimage = 'Images/missing.png'
        self.deceased.save(update_fields=['graveimage'])
        missing_file = self.client.get(
            reverse('PrivateGraveImageForRecord', kwargs={'pk': self.deceased.pk}),
        )

        self.assertEqual(missing_record.status_code, 404)
        self.assertEqual(missing_file.status_code, 404)

    def test_private_storage_rejects_traversal_and_does_not_change_public_product_urls(self):
        storage = PrivateGraveImageStorage()
        with self.assertRaises(SuspiciousFileOperation):
            storage.open('../../outside.png')

        traversal_request = RequestFactory().get('/deceased-search/grave-images/../../outside.png')
        traversal_request.user = self.active_user
        with self.assertRaises(Http404):
            private_grave_image(traversal_request, '../../outside.png')

        garden_photo = GardenDetail(Lot_Image='Images/public-garden.png')
        lot_photo = LotType(Lot_Photo='lot_photo/public-lot.png')
        self.assertNotIsInstance(GardenDetail._meta.get_field('Lot_Image').storage, PrivateGraveImageStorage)
        self.assertNotIsInstance(LotType._meta.get_field('Lot_Photo').storage, PrivateGraveImageStorage)
        self.assertIn('media/Images/public-garden.png', garden_photo.Lot_Image.url)
        self.assertIn('media/lot_photo/public-lot.png', lot_photo.Lot_Photo.url)

    def test_private_storage_url_routes_through_authenticated_image_view(self):
        self.assertEqual(
            self.deceased.graveimage.url,
            reverse('PrivateGraveImage', kwargs={'name': self.deceased.graveimage.name}),
        )


class PrivateGraveImageMigrationTests(TransactionTestCase):
    migrate_from = ('search', '0010_delete_lotname_deceasedinformation_date_created_and_more')
    migrate_to = ('search', '0011_private_grave_images')

    def setUp(self):
        self.public_directory = tempfile.TemporaryDirectory()
        self.private_directory = tempfile.TemporaryDirectory()
        settings_override = override_settings(
            MEDIA_ROOT=self.public_directory.name,
            PRIVATE_MEDIA_ROOT=self.private_directory.name,
        )
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.addCleanup(self.public_directory.cleanup)
        self.addCleanup(self.private_directory.cleanup)

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_failed_public_delete_remains_pending_for_startup_retry(self):
        public_storage = FileSystemStorage(location=self.public_directory.name)
        image_name = public_storage.save('Images/legacy-marker.png', ContentFile(PNG_IMAGE))
        record_public_grave_image_for_deletion(image_name)
        manifest = Path(self.private_directory.name) / PENDING_PUBLIC_GRAVE_IMAGE_DELETIONS

        original_delete = FileSystemStorage.delete

        def fail_image_delete(storage, name):
            if name == image_name:
                raise PermissionError('synthetic test restriction')
            return original_delete(storage, name)

        with patch.object(FileSystemStorage, 'delete', fail_image_delete):
            with self.assertRaises(PermissionError):
                cleanup_pending_public_grave_images()

        self.assertTrue(public_storage.exists(image_name))
        self.assertTrue(manifest.exists())

        self.assertEqual(cleanup_pending_public_grave_images(), 1)
        self.assertFalse(public_storage.exists(image_name))
        self.assertFalse(manifest.exists())

    def test_concurrent_cleanup_markers_do_not_overwrite_each_other(self):
        public_storage = FileSystemStorage(location=self.public_directory.name)
        image_names = [
            public_storage.save(f'Images/legacy-marker-{index}.png', ContentFile(PNG_IMAGE))
            for index in range(8)
        ]

        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(record_public_grave_image_for_deletion, image_names))

        pending_directory = Path(self.private_directory.name) / PENDING_PUBLIC_GRAVE_IMAGE_DELETIONS
        self.assertEqual(len(list(pending_directory.glob('*.json'))), len(image_names))
        self.assertEqual(cleanup_pending_public_grave_images(), len(image_names))
        self.assertTrue(all(not public_storage.exists(name) for name in image_names))

    def test_private_media_migration_skips_null_and_empty_image_references(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([
            self.migrate_from,
            ('procurement', '0001_initial'),
        ]).apps
        LocationModel = old_apps.get_model('search', 'Location')
        DeceasedModel = old_apps.get_model('search', 'DeceasedInformation')
        location = LocationModel.objects.create(grave_lot_id='01', grave_area='TEST GARDEN')

        records = []
        for image_name in (None, ''):
            records.append(DeceasedModel.objects.create(
                name=f'Synthetic Record {image_name!r}',
                born='1900-01-01',
                died='1980-01-01',
                location=location,
                graveimage=image_name,
            ))
        with connection.cursor() as cursor:
            cursor.execute(
                'UPDATE search_deceasedinformation SET graveimage = NULL WHERE id = %s',
                [records[0].pk],
            )
        self.assertCountEqual(
            DeceasedModel.objects.order_by('name').values_list('graveimage', flat=True),
            [None, ''],
        )

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([
            self.migrate_to,
            ('procurement', '0001_initial'),
        ]).apps
        DeceasedModel = new_apps.get_model('search', 'DeceasedInformation')
        migrated_references = list(
            DeceasedModel.objects.order_by('name').values_list('graveimage', flat=True)
        )
        self.assertCountEqual(migrated_references, [None, ''])

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        restored_apps = executor.loader.project_state([
            self.migrate_from,
            ('procurement', '0001_initial'),
        ]).apps
        DeceasedModel = restored_apps.get_model('search', 'DeceasedInformation')
        restored_references = list(
            DeceasedModel.objects.order_by('name').values_list('graveimage', flat=True)
        )
        self.assertCountEqual(restored_references, [None, ''])

    def test_migration_moves_existing_media_and_preserves_database_reference(self):
        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_from])
        old_apps = executor.loader.project_state([
            self.migrate_from,
            ('procurement', '0001_initial'),
        ]).apps
        LocationModel = old_apps.get_model('search', 'Location')
        DeceasedModel = old_apps.get_model('search', 'DeceasedInformation')
        GardenDetailModel = old_apps.get_model('procurement', 'GardenDetail')
        location = LocationModel.objects.create(grave_lot_id='01', grave_area='TEST GARDEN')
        image_name = 'Images/legacy-marker.png'
        DeceasedModel.objects.create(
            name='Synthetic Legacy Record',
            born='1900-01-01',
            died='1980-01-01',
            location=location,
            graveimage=image_name,
        )
        garden = GardenDetailModel.objects.create(
            Lot_Image=image_name,
            Garden_Name=location,
        )
        old_storage = FileSystemStorage(location=self.public_directory.name)
        old_storage.save(image_name, ContentFile(PNG_IMAGE))
        private_storage = PrivateGraveImageStorage()
        private_storage.save(image_name, ContentFile(b'pre-existing unrelated private file'))

        executor = MigrationExecutor(connection)
        executor.migrate([self.migrate_to])
        new_apps = executor.loader.project_state([
            self.migrate_to,
            ('procurement', '0001_initial'),
        ]).apps
        migrated_record = new_apps.get_model('search', 'DeceasedInformation').objects.get(
            name='Synthetic Legacy Record',
        )
        migrated_garden = new_apps.get_model('procurement', 'GardenDetail').objects.get(pk=garden.pk)

        self.assertNotEqual(migrated_record.graveimage, image_name)
        self.assertTrue(private_storage.exists(migrated_record.graveimage.name))
        self.assertFalse(old_storage.exists(image_name))
        with private_storage.open(migrated_record.graveimage.name, 'rb') as migrated_image:
            self.assertEqual(migrated_image.read(), PNG_IMAGE)
        with private_storage.open(image_name, 'rb') as unrelated_private_image:
            self.assertEqual(unrelated_private_image.read(), b'pre-existing unrelated private file')
        self.assertEqual(migrated_garden.Lot_Image.name, 'GardenImages/legacy-marker.png')
        self.assertTrue(old_storage.exists(migrated_garden.Lot_Image.name))
        with old_storage.open(migrated_garden.Lot_Image.name, 'rb') as garden_image:
            self.assertEqual(garden_image.read(), PNG_IMAGE)

        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

# Create your tests here.
