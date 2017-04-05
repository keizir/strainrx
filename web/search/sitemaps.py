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


class StrainsLetterPagedSitemap(Sitemap):
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        items = []
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                   'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']

        for l in letters:
            items.append({'url': 'search:strains_type_by_name', 'letter': l, 'variety': 'sativa'})
            items.append({'url': 'search:strains_type_by_name', 'letter': l, 'variety': 'indica'})
            items.append({'url': 'search:strains_type_by_name', 'letter': l, 'variety': 'hybrid'})

        return items

    def location(self, item):
        return reverse(item.get('url'), kwargs={'strain_variety': item.get('variety'), 'letter': item.get('letter')})

    def lastmod(self, obj):
        return datetime.now()
