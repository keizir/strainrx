import logging
import json
from web.es_service import BaseElasticService

logger = logging.getLogger(__name__)

class SearchElasticService(BaseElasticService):
    def _transform_strain_results(self, results):
        """

        :param results:
        :return:
        """
        strains = results.get('hits', {}).get('hits', [])
        processed_results = [s.get('_source', {}) for s in strains]
        return processed_results

    def query_strains_by_name(self, query, size=50):
        """

        :param query:
        :param size:
        :return:
        """
        # TODO - Kosta I'm 70% sure this should work but haven't fully tested it
        method = self.METHODS.get('POST')
        url = '{0}{1}{2}'.format(self.BASE_ELASTIC_URL, self.URLS.get('STRAIN'), '/flower')
        # build query dict
        query = {
            'term': {
                'name': {
                    'value': query
                }
            }
        }

        q = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_strain_results(q)

        return results