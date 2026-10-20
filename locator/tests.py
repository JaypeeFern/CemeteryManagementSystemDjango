from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from locator import views
from locator.views import _render_grave_map
from search.models import DeceasedInformation, Location


class GraveLocatorSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='locator-user',
            password='a-long-password-for-tests',
        )
        self.location = Location.objects.create(
            grave_lot_id='01',
            grave_area='GARDEN OF PETER',
        )
        self.deceased = DeceasedInformation.objects.create(
            name='Synthetic Test Record',
            born=date(1940, 1, 1),
            died=date(2020, 1, 1),
            location=self.location,
        )

    def tearDown(self):
        _render_grave_map.cache_clear()

    def test_grave_locator_and_search_routes_require_sign_in(self):
        protected_routes = [
            ('get', reverse('Search'), {}),
            ('get', reverse('tables'), {}),
            ('get', reverse('Locator'), {}),
            ('post', reverse('SearchResults'), {'q': 'Synthetic'}),
            ('get', reverse('SpecificSearch', args=[self.deceased.pk]), {}),
        ]

        for method, path, data in protected_routes:
            with self.subTest(path=path):
                response = getattr(self.client, method)(path, data)
                self.assertRedirects(
                    response,
                    f'{reverse("Home")}?next={path}',
                    fetch_redirect_response=False,
                )

    def test_inactive_account_cannot_access_deceased_records(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        self.client.force_login(self.user)

        response = self.client.get(reverse('Search'))

        self.assertRedirects(
            response,
            f'{reverse("Home")}?next={reverse("Search")}',
            fetch_redirect_response=False,
        )

    def test_authenticated_locator_renders_without_external_geocoding(self):
        self.client.force_login(self.user)
        with patch(
            'requests.sessions.Session.request',
            side_effect=AssertionError('Locator must not make outbound requests.'),
        ):
            response = self.client.get(reverse('Locator'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Grave Locator')

    def test_authenticated_specific_search_renders_without_external_geocoding(self):
        self.client.force_login(self.user)
        with patch(
            'requests.sessions.Session.request',
            side_effect=AssertionError('Locator must not make outbound requests.'),
        ):
            response = self.client.get(
                reverse('SpecificSearch', args=[self.deceased.pk]),
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Synthetic Test Record')

    def test_authenticated_specific_search_reuses_cached_map_for_same_garden(self):
        self.client.force_login(self.user)
        _render_grave_map.cache_clear()

        with patch(
            'locator.views.folium.Map',
            wraps=views.folium.Map,
        ) as map_factory:
            first_response = self.client.get(
                reverse('SpecificSearch', args=[self.deceased.pk]),
            )
            self.deceased.name = 'Updated Synthetic Test Record'
            self.deceased.save(update_fields=['name'])
            second_response = self.client.get(
                reverse('SpecificSearch', args=[self.deceased.pk]),
            )

        self.assertEqual(first_response.status_code, 200)
        self.assertContains(first_response, '9.767243416604591')
        self.assertEqual(second_response.status_code, 200)
        self.assertContains(second_response, 'Updated Synthetic Test Record')
        self.assertEqual(map_factory.call_count, 1)

    def test_authenticated_search_handles_empty_query_without_server_error(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('SearchResults'), {'q': '  '})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No matching records found')
