import json
import logging
from random import uniform

from web.es_service import BaseElasticService
from web.search.models import StrainImage, Strain

logger = logging.getLogger(__name__)


class SearchElasticService(BaseElasticService):
    def _transform_strain_results(self, results):
        """

        :param results:
        :return:
        """
        strains = results.get('hits', {}).get('hits', [])
        total = results.get('hits', {}).get('total', 0)
        processed_results = []

        for s in strains:
            source = s.get('_source', {})
            db_strain = Strain.objects.get(pk=source.get('id'))
            rating = "{0:.2f}".format(5 * uniform(0.3, 1))  # TODO retrieve overall rating for strain

            strain_image = StrainImage.objects.filter(strain=db_strain)[:1]
            # TODO  ^ need optimization here in order not to queru strain from DB to get actual image

            match_percentage = "{0:.2f}".format(100 * uniform(0.3, 1))  # TODO count match percentage with SRX

            processed_results.append({
                'id': source.get('id'),
                'internal_id': source.get('internal_id'),
                'name': source.get('name'),
                'strain_slug': source.get('strain_slug'),
                'variety': source.get('variety'),
                'category': source.get('category'),
                'rating': rating,
                'image': strain_image[0] if len(strain_image) > 0 else None,
                'match_percentage': match_percentage,
                'delivery_addresses': [  # TODO retrieve deliveries that has this strain for sale
                    {
                        'state': 'CA',
                        'city': 'Santa Monica',
                        'street1': 'Street 1 location',
                        'open': 'true',
                        'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                    },
                    {
                        'state': 'CA',
                        'city': 'Santa Monica',
                        'street1': 'Street 1 location',
                        'open': 'false',
                        'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                    },
                    {
                        'state': 'CA',
                        'city': 'Santa Monica',
                        'street1': 'Street 1 location',
                        'open': 'false',
                        'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                    }
                ]
            })

        response_data = {
            'list': processed_results,
            'total': total
        }

        return response_data

    def query_strains_by_name(self, query, size=50, start_from=0):
        """
        Get stains by name in a 'name contains' manner

        :param query: part of the word to search for
        :param size: size of returned data
        :param start_from: number of entity to start search from
        :return: { 'list': [], 'total': 0 }
        """

        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{0}{1}{2}{3}{4}{5}'.format(
            self.BASE_ELASTIC_URL,
            self.URLS.get('STRAIN'),
            '/_search?size=', size,
            '&from=', start_from)

        # build query dict
        query = {
            'query': {
                'match': {
                    'name': query.lower()
                }
            }
        }

        q = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_strain_results(q)

        return results
