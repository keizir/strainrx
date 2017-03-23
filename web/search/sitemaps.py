from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StrainRootSitemap(Sitemap):
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        return ['strains_root', 'strains_sativa_root', 'strains_indica_root', 'strains_hybrid_root']

    def location(self, item):
        return reverse(item)
