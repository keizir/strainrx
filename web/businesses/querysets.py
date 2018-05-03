from __future__ import unicode_literals, absolute_import

from django.db import models


class MenuItemQuerySet(models.QuerySet):

    def avg_8th_price(self, location):
        return self.filter(business_location=location)\
                   .aggregate(avg_price=models.Avg('price_eighth'))['avg_price']
