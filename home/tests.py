from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import patch
from home.views import _allow_limited_request
from django.urls import reverse


class LoginProtectionTests(TestCase):
    @patch('home.views._verify_recaptcha', return_value=False)
    @patch('home.views._allow_limited_request', return_value=True)
    @patch('home.views.LoginFormAuthentication')
    def test_invalid_captcha_stops_before_credential_authentication(self, login_form, allow_limited_request, verify_recaptcha):
        response = self.client.post(
            reverse('Login'),
            {
                'username': 'unknown',
                'password': 'wrong-password',
                'g-recaptcha-response': 'invalid-token',
            },
        )

        self.assertEqual(response.status_code, 302)
        login_form.assert_not_called()
        allow_limited_request.assert_called_once()
        verify_recaptcha.assert_called_once_with('invalid-token')

    @patch('home.views._allow_limited_request')
    @patch('home.views._verify_recaptcha')
    def test_missing_login_captcha_is_rejected_without_google_request(self, verify_recaptcha, allow_limited_request):
        response = self.client.post(
            reverse('Login'),
            {'username': 'unknown', 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 302)
        allow_limited_request.assert_not_called()
        verify_recaptcha.assert_not_called()

    @patch('home.views._allow_limited_request')
    @patch('home.views._verify_recaptcha')
    def test_oversized_login_captcha_is_rejected_without_google_request(self, verify_recaptcha, allow_limited_request):
        response = self.client.post(
            reverse('Login'),
            {
                'username': 'unknown',
                'password': 'wrong-password',
                'g-recaptcha-response': 'x' * 8193,
            },
        )

        self.assertEqual(response.status_code, 302)
        allow_limited_request.assert_not_called()
        verify_recaptcha.assert_not_called()

    def test_login_endpoint_only_accepts_post_requests(self):
        response = self.client.get(reverse('Login'))
        self.assertEqual(response.status_code, 405)

    def test_logout_endpoint_only_accepts_post_requests(self):
        response = self.client.get(reverse('Logout'))
        self.assertEqual(response.status_code, 405)


class RegistrationProtectionTests(TestCase):
    @patch('home.views._allow_limited_request', return_value=False)
    @patch('home.views._verify_recaptcha')
    def test_signup_captcha_verification_is_throttled_before_google(self, verify_recaptcha, allow_request):
        response = self.client.post(
            reverse('Register'),
            {
                'username': 'new-user',
                'password1': 'strong-password-for-test-user',
                'password2': 'strong-password-for-test-user',
                'g-recaptcha-response': 'unverified-token',
            },
        )

        self.assertEqual(response.status_code, 302)
        allow_request.assert_called_once()
        verify_recaptcha.assert_not_called()
        self.assertFalse(User.objects.filter(username='new-user').exists())

    @patch('home.views._verify_recaptcha', return_value=False)
    @patch('home.views._allow_limited_request', return_value=True)
    def test_signup_requires_valid_captcha(self, allow_request, verify_recaptcha):
        response = self.client.post(
            reverse('Register'),
            {
                'username': 'new-user',
                'password1': 'strong-password-for-test-user',
                'password2': 'strong-password-for-test-user',
                'g-recaptcha-response': 'invalid-token',
            },
        )

        self.assertEqual(response.status_code, 302)
        allow_request.assert_called_once()
        verify_recaptcha.assert_called_once_with('invalid-token')
        self.assertFalse(User.objects.filter(username='new-user').exists())

    @patch('home.views._allow_limited_request', side_effect=[True, False])
    @patch('home.views._verify_recaptcha', return_value=True)
    def test_signup_creation_quota_applies_after_valid_captcha(self, verify_recaptcha, allow_request):
        response = self.client.post(
            reverse('Register'),
            {
                'first_name': 'New User',
                'username': 'new.user.unique',
                'password1': 'G7!mQ2#vL9@wX4rP',
                'password2': 'G7!mQ2#vL9@wX4rP',
                'g-recaptcha-response': 'valid-token',
            },
        )

        self.assertEqual(response.status_code, 302)
        verify_recaptcha.assert_called_once_with('valid-token')
        self.assertEqual(allow_request.call_count, 2)
        self.assertFalse(User.objects.filter(username='new.user.unique').exists())

    @patch('home.views._allow_limited_request', return_value=True)
    @patch('home.views._verify_recaptcha', return_value=True)
    def test_new_accounts_wait_for_staff_approval_before_sign_in(self, verify_recaptcha, allow_request):
        response = self.client.post(
            reverse('Register'),
            {
                'first_name': 'Pending User',
                'username': 'pending.user',
                'password1': 'G7!mQ2#vL9@wX4rP',
                'password2': 'G7!mQ2#vL9@wX4rP',
                'g-recaptcha-response': 'valid-token',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='pending.user')
        self.assertFalse(user.is_active)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_signup_endpoint_only_accepts_post_requests(self):
        response = self.client.get(reverse('Register'))
        self.assertEqual(response.status_code, 405)

    @patch('home.views._allow_limited_request')
    @patch('home.views._verify_recaptcha')
    def test_oversized_signup_captcha_is_rejected_before_google(self, verify_recaptcha, allow_request):
        response = self.client.post(
            reverse('Register'),
            {
                'username': 'new-user',
                'password1': 'strong-password-for-test-user',
                'password2': 'strong-password-for-test-user',
                'g-recaptcha-response': 'x' * 8193,
            },
        )

        self.assertEqual(response.status_code, 302)
        allow_request.assert_not_called()
        verify_recaptcha.assert_not_called()

    @patch('home.views.get_client_ip_address', return_value='203.0.113.42')
    def test_fixed_window_throttle_stops_after_configured_limit(self, get_client_ip):
        request = RequestFactory().post('/')

        self.assertTrue(_allow_limited_request(request, 'test', limit=2, window_seconds=600))
        self.assertTrue(_allow_limited_request(request, 'test', limit=2, window_seconds=600))
        self.assertFalse(_allow_limited_request(request, 'test', limit=2, window_seconds=600))
        self.assertEqual(get_client_ip.call_count, 3)

    @patch('home.views.get_client_ip_address', return_value=None)
    def test_throttle_falls_back_to_peer_address_when_proxy_ip_unavailable(self, get_client_ip):
        request = RequestFactory().post('/')

        self.assertTrue(_allow_limited_request(request, 'fallback', limit=1, window_seconds=600))
        get_client_ip.assert_called_once_with(request)
