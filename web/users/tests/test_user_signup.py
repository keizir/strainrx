from django.contrib.auth import get_user_model
from django.utils import lorem_ipsum
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.search.models import UserSearch
from web.users.emails import EmailService
from web.users.models import UserLocation


class UserSignUpWizardTestCase(APITestCase):

    def setUp(self):
        self.url = reverse('users_api:signup')
        self.data = {
            'is_age_verified': True,
            'is_terms_accepted': True,
            'last_name': lorem_ipsum.words(1),
            'pwd': '123456@', 'pwd2': '123456@',
            'first_name': lorem_ipsum.words(1),
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'location': {
                'zipcode': '65000', 'street1': lorem_ipsum.words(1),
                'city': lorem_ipsum.words(1), 'state': lorem_ipsum.words(1), 'location_raw': {},
                'lat': 46, 'lng': 30
            },
            'search_criteria': {
                'step4': {'skipped': True},
                'step1': {'hybrid': True, 'indica': False, 'sativa': False},
                'step2': {'effects': [{'value': 1, 'name': 'uplifted'}]},
                'step3': {'skipped': True}}
        }

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_without_search_settings(self, _):
        self.data.pop('search_criteria')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 0)

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_search_settings(self, _):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 1)
        self.assertEqual(UserSearch.objects.first().effects, [{'value': 1, 'name': 'uplifted'}])

    @patch.object(EmailService, 'send_confirmation_email', return_value=None)
    def test_signup_with_not_completed_search_settings(self, _):
        self.data['search_criteria'].pop('step3')
        self.data['search_criteria'].pop('step4')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 0)
