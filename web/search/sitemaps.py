from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StrainRootSitemap(Sitemap):
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['search:strains_root', 'search:strains_sativa_root', 'search:strains_indica_root',
                'search:strains_hybrid_root']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return datetime.now()
