import random

import pytz
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import lorem_ipsum
from mock import patch
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, force_authenticate, APIClient

from web.search.models import UserSearch
from web.users.emails import EmailService
from web.users.models import UserLocation, GENDER
from web.users.tests.factories import UserFactory, TEST_USER_PASSWORD


class UserDetailTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('users_api:user-detail', args=(self.user.pk,))
        self.data = {
            'name': lorem_ipsum.words(1),
            'last_name': lorem_ipsum.words(1),
            'first_name': lorem_ipsum.words(1),
            'email': '{}@example.com'.format(lorem_ipsum.words(1)),
            'birth_month': 'jan', 'birth_day': "10", 'birth_year': "1989",
            'gender': GENDER[1][0],
            'timezone': random.choice(pytz.common_timezones),
            'location': {
                'zipcode': '65000', 'street1': lorem_ipsum.words(1),
                'city': lorem_ipsum.words(1), 'state': lorem_ipsum.words(1), 'location_raw': {},
                'lat': 46, 'lng': 30
            }
        }

    def test_update_user_detail(self):
        """
        User successfully update his account
        """
        self.client.login(username=self.user.email, password=TEST_USER_PASSWORD)
        response = self.client.put(self.url, self.data, format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.json())
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(UserLocation.objects.count(), 1)
        self.assertEqual(UserSearch.objects.count(), 0)

    def test_not_owner(self):
        """
        User
        """

    def test_anonymous(self):
        """

        """