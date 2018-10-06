from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.db.models import Q

from web.businesses.models import BusinessLocation, State, City


class BusinessLocationSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return BusinessLocation.objects\
            .filter(Q(removed_date=None) & Q(Q(dispensary=True) | Q(delivery=True)))\
            .select_related('state_fk', 'city_fk')

    def lastmod(self, obj):
        return datetime.now()


class StateRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return State.objects.all()

    def lastmod(self, obj):
        return datetime.now()


class CityRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return City.objects.all()

    def lastmod(self, obj):
        return datetime.now()


class DispensariesRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['businesses:dispensaries_list', 'businesses:growers_list']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return datetime.now()


class GrowHouseSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return BusinessLocation.objects\
            .filter(removed_date=None, grow_house=True)\
            .select_related('state_fk', 'city_fk')

    def lastmod(self, obj):
        return datetime.now()

    def location(self, obj):
        return reverse('businesses:grower_info', kwargs={
            'state': obj.state_fk.abbreviation.lower(),
            'city_slug': obj.city_fk.full_name_slug,
            'slug_name': obj.slug_name
        })


class GrowHouseStateRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return State.objects.all()

    def lastmod(self, obj):
        return datetime.now()

    def location(self, obj):
        return reverse('businesses:growers_state_list',
                       kwargs={'state': obj.abbreviation.lower()})


class GrowHouseCityRootSitemap(Sitemap):
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return City.objects.all()

    def lastmod(self, obj):
        return datetime.now()

    def location(self, obj):
        return reverse('businesses:growers_city_list',
                       kwargs={'state': obj.state.abbreviation.lower(), 'city_slug': obj.full_name_slug})
