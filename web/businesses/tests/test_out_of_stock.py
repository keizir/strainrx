from django.utils import timezone
from mock import patch
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from web.businesses.emails import EmailService
from web.businesses.models import ReportOutOfStock
from web.businesses.tests.factories import BusinessLocationMenuItemFactory
from web.users.tests.factories import UserFactory


class OutOfStockTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.menu = BusinessLocationMenuItemFactory()
        self.url = reverse('businesses_api:business_location_report_out_of_stock',
                           args=(self.menu.business_location.business_id, self.menu.pk))

    def test_user_not_authorized(self):
        """
        Anonymous user does not have access to the analytics page
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    def test_report_out_of_stock(self, _):
        """
        User report out of stock
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 1)
        report = ReportOutOfStock.objects.first()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    def test_report_out_of_stock_second_time(self, _):
        """
        User report out of stock second time in 7 days after first report
        """
        first_report = ReportOutOfStock.objects.create(menu_item=self.menu, user=self.user)
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 2)

        report = ReportOutOfStock.objects.last()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)

        first_report.refresh_from_db()
        self.assertFalse(first_report.is_active)

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.removed_date.date(), timezone.now().date())

    @patch.object(EmailService, 'send_report_out_of_stock', return_value=None)
    def test_report_out_of_stock_second_time_more_then_7_days(self, _):
        """
        User report out of stock second time more the 7 days after first report
        """
        first_report = ReportOutOfStock.objects.create(menu_item=self.menu, user=self.user,
                                                       created=timezone.now()-timezone.timedelta(days=8))
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReportOutOfStock.objects.count(), 2)

        report = ReportOutOfStock.objects.last()
        self.assertEqual(report.user, self.user)
        self.assertEqual(report.menu_item, self.menu)

        first_report.refresh_from_db()
        self.assertTrue(first_report.is_active)

        self.menu.refresh_from_db()
        self.assertEqual(self.menu.removed_date, None)
