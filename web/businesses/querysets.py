from __future__ import unicode_literals, absolute_import

from django.db import models
from django.conf import settings
from django.utils import timezone


class MenuItemQuerySet(models.QuerySet):

    def avg_8th_price(self, location):
        return self.filter(business_location=location) \
            .aggregate(avg_price=models.Avg('price_eighth'))['avg_price']

    def reports(self):
        return self.annotate(report_count=models.Sum(
            models.Case(
                models.When(reports__count__gte=2,
                            reports__is_active=True,
                            reports__start_timer__gte=timezone.now() - timezone.timedelta(
                                days=settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK),
                            then=1),
                default=0,
                output_field=models.IntegerField(),
            )
        ))


class ReportOutOfStockQuerySet(models.QuerySet):

    def is_out_of_stock_reports(self, menu):
        """
        Check if menu item was reported as out of stock two times
        :param menu: BusinessLocationMenuItem instance
        :return: boolean
        """
        return self.filter(
            menu_item=menu, count=2, is_active=True,
            start_timer__gte=timezone.now() - timezone.timedelta(
                days=settings.PERIOD_BLOCK_MENU_ITEM_OUT_OF_STOCK)).exists()


class UserFavoriteLocationQuerySet(models.QuerySet):

    def get_user_favorites(self, user):
        return self.filter(created_by=user).order_by('-created_date')
