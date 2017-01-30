from datetime import datetime

from django.contrib.sitemaps import Sitemap

from web.businesses.models import BusinessLocation


class BusinessLocationSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return BusinessLocation.objects.filter(removed_date=None)

    def lastmod(self, obj):
        return datetime.now()
