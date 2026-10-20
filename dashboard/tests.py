from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.files.uploadhandler import StopUpload
from django.test import RequestFactory
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from dashboard.forms import (
    DeceasedInfoForm,
    GardenDetailForm,
    LotTypeForm,
    UpdateGraveImage,
    UpdateStaffForm,
    UpdateUserForm,
)
from dashboard.upload_validation import MAX_UPLOAD_SIZE_BYTES, validate_upload_size
from dashboard.upload_handlers import UploadSizeLimitHandler


class DashboardAuthorizationTests(TestCase):
    def test_dashboard_routes_reject_anonymous_users(self):
        protected_routes = [
            ('Dashboard', {}),
            ('FilterMonth', {}),
            ('FilterYear', {}),
            ('Dash_Search', {}),
            ('Dash_Add', {}),
            ('Update', {'pk': 1}),
            ('Delete', {'pk': '1'}),
            ('ImportCSV', {}),
            ('GraveImages', {}),
            ('UpdateImage', {'pk': 1}),
            ('DeleteImage', {'pk': '1'}),
            ('Locations', {}),
            ('AddLocation', {}),
            ('UpdateLocation', {'pk': 1}),
            ('DeleteLocation', {'pk': 1}),
            ('Customer', {}),
            ('AddCustomer', {}),
            ('UpdateCustomer', {'pk': 1}),
            ('DeleteCustomer', {'pk': 1}),
            ('GardenDetails', {}),
            ('AddGarden', {}),
            ('UpdateGarden', {'pk': 1}),
            ('DeleteGarden', {'pk': 1}),
            ('GardenImages', {}),
            ('DeleteGardenImage', {'pk': 1}),
            ('ImportCSV', {}),
            ('LotTypes', {}),
            ('AddLotType', {}),
            ('UpdateLotType', {'pk': 1}),
            ('DeleteLotType', {'pk': 1}),
            ('SystemUsers', {}),
            ('AddUser', {}),
            ('UpdateUser', {'pk': 1}),
            ('DeleteUser', {'pk': 1}),
            ('SystemStaff', {}),
            ('ImportCSV', {}),
            ('AddStaff', {}),
            ('UpdateStaff', {'pk': 1}),
            ('DeleteStaff', {'pk': 1}),
        ]

        for route_name, kwargs in protected_routes:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name, kwargs=kwargs))
                self.assertEqual(response.status_code, 302)

    def test_staff_cannot_manage_privileged_accounts_or_images(self):
        staff_user = User.objects.create_user(
            username='staff-user',
            password='a-long-password-for-tests',
            is_staff=True,
        )
        self.client.force_login(staff_user)

        for route_name, kwargs, expected_status in [
            ('SystemStaff', {}, 302),
            ('AddStaff', {}, 302),
            ('UpdateStaff', {'pk': staff_user.pk}, 302),
            ('DeleteStaff', {'pk': staff_user.pk}, 403),
            ('Delete', {'pk': '1'}, 403),
            ('DeleteLocation', {'pk': 1}, 403),
            ('DeleteCustomer', {'pk': 1}, 403),
            ('DeleteGarden', {'pk': 1}, 403),
            ('DeleteLotType', {'pk': 1}, 403),
            ('DeleteUser', {'pk': 1}, 403),
            ('DeleteImage', {'pk': '1'}, 302),
            ('DeleteGardenImage', {'pk': 1}, 302),
        ]:
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name, kwargs=kwargs))
                self.assertEqual(response.status_code, expected_status)

    def test_staff_cannot_update_or_delete_staff_through_regular_user_routes(self):
        staff_user = User.objects.create_user(
            username='staff-user',
            password='a-long-password-for-tests',
            is_staff=True,
        )
        superuser = User.objects.create_superuser(
            username='admin-user',
            email='admin@example.invalid',
            password='another-long-password-for-tests',
        )
        self.client.force_login(staff_user)

        update_response = self.client.get(reverse('UpdateUser', kwargs={'pk': superuser.pk}))
        delete_response = self.client.get(reverse('DeleteUser', kwargs={'pk': superuser.pk}))

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 403)

    def test_csv_import_rejects_get_and_post_without_file(self):
        administrator = User.objects.create_superuser(
            username='csv-admin',
            email='csv-admin@example.invalid',
            password='a-long-password-for-tests',
        )
        self.client.force_login(administrator)

        get_response = self.client.get(reverse('ImportCSV'))
        post_response = self.client.post(reverse('ImportCSV'))

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(post_response.status_code, 400)

    def test_csv_import_rejects_oversized_upload_before_parsing(self):
        administrator = User.objects.create_superuser(
            username='csv-size-admin',
            email='csv-size-admin@example.invalid',
            password='a-long-password-for-tests',
        )
        self.client.force_login(administrator)
        csv_file = SimpleUploadedFile(
            'too-large.csv',
            b'x' * (MAX_UPLOAD_SIZE_BYTES + 1),
            content_type='text/csv',
        )

        response = self.client.post(reverse('ImportCSV'), {'csv_file': csv_file})

        self.assertEqual(response.status_code, 413)

    def test_dashboard_image_forms_reject_files_over_the_size_limit(self):
        oversized_image = SimpleUploadedFile(
            'too-large.jpg',
            b'x' * (MAX_UPLOAD_SIZE_BYTES + 1),
            content_type='image/jpeg',
        )
        image_fields = (
            (DeceasedInfoForm, 'graveimage'),
            (UpdateGraveImage, 'graveimage'),
            (GardenDetailForm, 'Lot_Image'),
            (LotTypeForm, 'Lot_Photo'),
        )

        for form_class, field_name in image_fields:
            with self.subTest(form=form_class.__name__, field=field_name):
                self.assertIn(validate_upload_size, form_class().fields[field_name].validators)
                with self.assertRaises(ValidationError):
                    validate_upload_size(oversized_image)

    def test_streaming_upload_handler_stops_file_at_the_configured_limit(self):
        request = RequestFactory().post('/')
        handler = UploadSizeLimitHandler(request)
        handler.new_file('upload', 'too-large.bin', 'application/octet-stream', None, None, None)

        with self.assertRaises(StopUpload):
            handler.receive_data_chunk(b'x' * (MAX_UPLOAD_SIZE_BYTES + 1), 0)

        self.assertTrue(request.upload_too_large)


class AccountSessionRevocationTests(TestCase):
    def _assert_account_status_change_revokes_old_session(self, route_name, target_user, account_data):
        administrator = User.objects.create_superuser(
            username=f'{route_name.lower()}-admin',
            email=f'{route_name.lower()}-admin@example.invalid',
            password='an-administrator-password-for-tests',
        )
        self.client.force_login(administrator)

        target_client = Client()
        target_client.force_login(target_user)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 200)

        update_url = reverse(route_name, kwargs={'pk': target_user.pk})
        deactivate_response = self.client.post(update_url, account_data)
        self.assertEqual(deactivate_response.status_code, 302)
        self.assertFalse(User.objects.get(pk=target_user.pk).is_active)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 302)

        reactivate_response = self.client.post(update_url, {**account_data, 'is_active': 'on'})
        self.assertEqual(reactivate_response.status_code, 302)
        self.assertTrue(User.objects.get(pk=target_user.pk).is_active)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 302)

    def test_update_user_revokes_previous_sessions_when_active_status_changes(self):
        user = User.objects.create_user(username='revoked-user', password='a-user-password-for-tests')

        self._assert_account_status_change_revokes_old_session(
            'UpdateUser',
            user,
            {'username': user.username, 'first_name': user.first_name},
        )

    def test_update_staff_revokes_previous_sessions_when_active_status_changes(self):
        staff_user = User.objects.create_user(
            username='revoked-staff-user',
            password='a-staff-password-for-tests',
            is_staff=True,
        )

        self._assert_account_status_change_revokes_old_session(
            'UpdateStaff',
            staff_user,
            {
                'username': staff_user.username,
                'first_name': staff_user.first_name,
                'is_staff': 'on',
            },
        )

    def test_django_admin_revokes_previous_sessions_when_active_status_changes(self):
        administrator = User.objects.create_superuser(
            username='admin-session-revocation-admin',
            email='admin-session-revocation-admin@example.invalid',
            password='an-administrator-password-for-tests',
        )
        user = User.objects.create_user(
            username='admin-revoked-user',
            password='a-user-password-for-tests',
        )
        self.client.force_login(administrator)
        target_client = Client()
        target_client.force_login(user)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 200)

        update_url = reverse('admin:auth_user_change', kwargs={'object_id': user.pk})
        account_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_joined_0': user.date_joined.strftime('%Y-%m-%d'),
            'date_joined_1': user.date_joined.strftime('%H:%M:%S'),
        }
        deactivate_response = self.client.post(update_url, account_data)
        self.assertEqual(deactivate_response.status_code, 302)
        self.assertFalse(User.objects.get(pk=user.pk).is_active)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 302)

        reactivate_response = self.client.post(update_url, {**account_data, 'is_active': 'on'})
        self.assertEqual(reactivate_response.status_code, 302)
        self.assertTrue(User.objects.get(pk=user.pk).is_active)
        self.assertEqual(target_client.get(reverse('Search')).status_code, 302)


class AccountPasswordPolicyTests(TestCase):
    def test_regular_account_password_reset_uses_configured_validators(self):
        user = User.objects.create_user(username='regular-user', password='old-password-value')
        form = UpdateUserForm(
            {'username': user.username, 'first_name': '', 'is_active': 'on', 'new_password': '123'},
            instance=user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)

    def test_staff_password_reset_uses_configured_validators(self):
        user = User.objects.create_user(username='staff-user', password='old-password-value', is_staff=True)
        form = UpdateStaffForm(
            {
                'username': user.username,
                'first_name': '',
                'is_active': 'on',
                'is_staff': 'on',
                'is_superuser': '',
                'new_password': '123',
            },
            instance=user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_password', form.errors)
