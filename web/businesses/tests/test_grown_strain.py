from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.businesses.models import BusinessLocationGrownStrainItem
from web.businesses.tests.factories import BusinessLocationFactory, BusinessFactory, \
    BusinessLocationGrownStrainItemFactory
from web.search.tests.factories import StrainFactory
from web.users.tests.factories import BusinessUserFactory


class GrownStrainTestCase(APITestCase):

    def setUp(self):
        self.user = BusinessUserFactory()
        self.business = BusinessFactory(created_by=self.user)
        self.location = BusinessLocationFactory(business=self.business, grow_house=True)
        self.strain = StrainFactory()

        self.url = reverse('businesses_api:business_location:grown_strain-list',
                           args=(self.location.business_id, self.location.pk))

        self.data = {'strain': self.strain.pk}

    def test_permissions(self):
        """
        Only owner or staff of business can CRUD grown strain items
        """
        # Anonymous user
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Not owner
        self.client.force_login(self.user)
        location = BusinessLocationFactory(grow_house=True)
        url = reverse('businesses_api:business_location:grown_strain-list',
                      args=(location.business_id, location.pk))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Allow any for readonly operations
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add(self):
        """
        User successfully create grown strain
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessLocationGrownStrainItem.objects.count(), 1)

        grown_strain = BusinessLocationGrownStrainItem.objects.first()
        self.assertEqual(grown_strain.business_location_id, self.location.pk)
        self.assertEqual(grown_strain.strain_id, self.strain.pk)

        self.assertEqual(response.json(), {
            'id': grown_strain.id,
            'strain': grown_strain.strain.id,
            'strain_name': grown_strain.strain.name,
            'strain_variety': grown_strain.strain.variety,
            'url': grown_strain.strain.get_absolute_url(),
        })

    def test_add_same_menu_item(self):
        """
        User try to add already existed grown strain item but edit already existed
        """
        menu = BusinessLocationGrownStrainItemFactory(strain=self.strain, business_location=self.location)

        self.client.force_login(self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessLocationGrownStrainItem.objects.count(), 1)

        menu.refresh_from_db()
        self.assertEqual(menu.business_location_id, self.location.pk)
        self.assertEqual(menu.strain_id, self.strain.pk)

        self.assertEqual(response.json(), {
            'id': menu.id,
            'strain': menu.strain.id,
            'strain_name': menu.strain.name,
            'strain_variety': menu.strain.variety,
            'url': menu.strain.get_absolute_url(),
        })

    def test_add_with_wrong_data(self):
        """
        User submit wrong data and get error message
        """
        data = {
            'strain': self.strain.pk + 1000
        }

        self.client.force_login(self.user)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BusinessLocationGrownStrainItem.objects.count(), 0)
        self.assertEqual(response.json(), {
            'strain': ['Invalid pk "{}" - object does not exist.'.format(data['strain'])]
        })

    def test_list(self):
        """
        User get grown strain list
        """
        BusinessLocationGrownStrainItemFactory.create_batch(5)
        menu1 = BusinessLocationGrownStrainItemFactory(business_location=self.location, strain__name='test1')
        menu2 = BusinessLocationGrownStrainItemFactory(business_location=self.location, strain__name='test2')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [
            {
                'id': menu1.id,
                'strain': menu1.strain.id,
                'strain_name': menu1.strain.name,
                'strain_variety': menu1.strain.variety,
                'url': menu1.strain.get_absolute_url(),
            }, {
                'id': menu2.id,
                'strain': menu2.strain.id,
                'strain_name': menu2.strain.name,
                'strain_variety': menu2.strain.variety,
                'url': menu2.strain.get_absolute_url(),
            }
        ])

    def test_delete(self, *args):
        """
        User successfully delete item
        """
        self.client.force_login(self.user)
        menu = BusinessLocationGrownStrainItemFactory(business_location=self.location)
        url = reverse('businesses_api:business_location:grown_strain-detail',
                      args=(self.location.business_id, self.location.pk, menu.pk))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BusinessLocationGrownStrainItem.objects.count(), 0)

    def test_delete_wrong_item(self, *args):
        """
        User try to delete not existing item and receive error
        """
        self.client.force_login(self.user)
        menu = BusinessLocationGrownStrainItemFactory()
        url = reverse('businesses_api:business_location:grown_strain-detail',
                      args=(self.location.business_id, self.location.pk, menu.pk))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(BusinessLocationGrownStrainItem.objects.count(), 1)
