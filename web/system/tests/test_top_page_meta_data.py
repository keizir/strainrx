from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from web.system.tests.factories import TopPageMetaDataFactory


class TopPageMetaDataTestCase(APITestCase):

    def test_meta_home_page(self):
        """
        Meta data displayed properly on home page
        """
        pag_meta = TopPageMetaDataFactory(path='/')
        url = reverse('home')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, '<title>{} - StrainRx</title>'.format(pag_meta.meta_title))
        self.assertContains(response, '<meta name="keywords" content="{}">'.format(pag_meta.meta_keywords))
        self.assertContains(response, '<meta name="description" content="{}">'.format(pag_meta.meta_desc))
        self.assertContains(response, '<meta property="og:type" content="{}" />'.format(pag_meta.og_type))
        self.assertContains(response, '<meta property="og:title" content="{}" />'.format(pag_meta.og_title))
        self.assertContains(response, '<meta property="og:description" content="{}" />'.format(pag_meta.og_description))
        self.assertContains(response, '<meta property="fb:app_id" content="{}" />'.format(pag_meta.fb_app_id))
        self.assertContains(response, '<meta name="twitter:card" content="{}">'.format(pag_meta.twitter_card))
        self.assertContains(response, '<meta name="twitter:author" content="{}">'.format(pag_meta.twitter_author))
        self.assertContains(response, '<meta name="twitter:site" content="{}">'.format(pag_meta.twitter_site))

    def test_meta_dispensary_page(self):
        """
        Meta data displayed properly on dispensary page
        """
        pag_meta = TopPageMetaDataFactory(path='/dispensaries/')
        url = reverse('businesses:dispensaries_list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, '<title>{} - StrainRx</title>'.format(pag_meta.meta_title))
        self.assertContains(response, '<meta name="keywords" content="{}">'.format(pag_meta.meta_keywords))
        self.assertContains(response, '<meta name="description" content="{}">'.format(pag_meta.meta_desc))
        self.assertContains(response, '<meta property="og:type" content="{}" />'.format(pag_meta.og_type))
        self.assertContains(response, '<meta property="og:title" content="{}" />'.format(pag_meta.og_title))
        self.assertContains(response, '<meta property="og:description" content="{}" />'.format(pag_meta.og_description))
        self.assertContains(response, '<meta property="fb:app_id" content="{}" />'.format(pag_meta.fb_app_id))
        self.assertContains(response, '<meta name="twitter:card" content="{}">'.format(pag_meta.twitter_card))
        self.assertContains(response, '<meta name="twitter:author" content="{}">'.format(pag_meta.twitter_author))
        self.assertContains(response, '<meta name="twitter:site" content="{}">'.format(pag_meta.twitter_site))
