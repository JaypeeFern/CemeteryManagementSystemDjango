from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from procurement.models import Customer, GardenDetail, LotType
from search.models import Location


class ReservationSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            password='a-long-password-for-tests',
        )
        self.other_user = User.objects.create_user(
            username='other-owner',
            password='another-long-password-for-tests',
        )
        location = Location.objects.create(grave_lot_id='1', grave_area='Test Garden')
        lot_type = LotType.objects.create(Lot_Name='Test Lot')
        self.garden = GardenDetail.objects.create(
            Garden_Name=location,
            Available_Space=1,
        )
        self.garden.Lot_Type.add(lot_type)
        self.lot_type = lot_type
        self.reservation_data = {
            'first_Name': 'Test',
            'last_Name': 'Customer',
            'contact_Number': '0000000000',
            'deceased_Name': 'Test Person',
            'born_Date': '1950-01-01',
            'died_Date': '2020-01-01',
            'burial_Schedule': '2020-01-02',
            'chosen_Lot': self.garden.pk,
            'chosen_Lot_Type': self.lot_type.pk,
        }

    def test_anonymous_procurement_page_has_no_customer_data(self):
        response = self.client.get(reverse('Procurement'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['data4']), [])

    def test_reservation_requires_login(self):
        response = self.client.post(
            reverse('customerForm'),
            {**self.reservation_data, 'submitted_by': self.user.pk},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.count(), 0)
        self.garden.refresh_from_db()
        self.assertEqual(self.garden.Available_Space, 1)

    def test_reservation_owner_comes_from_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('customerForm'),
            {
                **self.reservation_data,
                'submitted_by': self.other_user.pk,
                'status': 'true',
            },
        )

        self.assertEqual(response.status_code, 302)
        customer = Customer.objects.get()
        self.assertEqual(customer.submitted_by, self.user)
        self.assertFalse(customer.status)
        self.garden.refresh_from_db()
        self.assertEqual(self.garden.Available_Space, 0)

    def test_reservation_rejects_lot_type_not_attached_to_selected_garden(self):
        unrelated_type = LotType.objects.create(Lot_Name='Unrelated Lot')
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('customerForm'),
            {**self.reservation_data, 'chosen_Lot_Type': unrelated_type.pk},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Customer.objects.count(), 0)
        self.garden.refresh_from_db()
        self.assertEqual(self.garden.Available_Space, 1)
