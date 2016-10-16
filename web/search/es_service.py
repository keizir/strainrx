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

            processed_results.append({
                'id': source.get('id'),
                'name': source.get('name'),
                'strain_slug': source.get('strain_slug'),
                'variety': source.get('variety'),
                'category': source.get('category'),
                'rating': rating,
                'image_url': strain_image[0].image.url if len(strain_image) > 0 else None,
                'match_percentage': "{0:.2f}".format(s.get('_score')),
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

    def query_strain_srx_score(self, criteria, size=50, start_from=0):
        """
            Return strains ranked by SRX score
        """
        if start_from is None:
            start_from = 0

        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search?size={size}&from={start_from}'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('STRAIN'),
            type='flower',
            size=size,
            start_from=start_from
        )

        query = self.build_srx_score_es_query(criteria)
        es_response = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_strain_results(es_response)
        return results

    def build_srx_score_es_query(self, criteria):
        # TODO not forget to use strain type at the end
        criteria_strain_types = criteria.get('strain_types')

        effects_data = self.parse_criteria_data(criteria.get('effects'))
        benefits_data = self.parse_criteria_data(criteria.get('benefits'))
        side_effects_data = self.parse_criteria_data(criteria.get('side_effects'))

        return {
            "query": {
                "function_score": {
                    "query": {
                        "match_all": {}
                    },
                    "functions": [
                        {
                            "script_score": {
                                "params": {
                                    "effectSum": effects_data.get('sum'),
                                    "benefitSum": benefits_data.get('sum'),
                                    "userEffects": effects_data.get('data'),
                                    "userBenefits": benefits_data.get('data'),
                                    "userNegEffects": side_effects_data.get('data')
                                },
                                "script": "def psa=effectSum+benefitSum;def benefitPoints=0;def effectPoints=0;def negEffectPoints=0;def distLookup=[(-5):-1,(-4):-0.8,(-3):-0.51,(-2):-0.33,(-1):-0.14,(0):0,(1):-0.01,(2):-0.01,(3):-0.01,(4):-0.01,(5):-0.01];for(e in userEffects){e=e.key;def strainE=_source['effects'][e];def userE=userEffects[e];def effectBonus=0.0;dist=strainE-userE;npe=distLookup[dist]*userE;if(userE==strainE){switch(strainE){case 3:effectBonus=0.3;break;case 4:effectBonus=0.5;break;case 5:effectBonus=1.0;break;}};effectPoints+=effectBonus+userE+npe;};for(b in userBenefits){b=b.key;def strainB=_source['benefits'][b];def userB=userBenefits[b];def benefitBonus=0.0;dist=strainB-userB;npb=distLookup[dist]*userB;if(userB==strainB){switch(strainB){case 3:benefitBonus=0.3;break;case 4:benefitBonus=0.5;break;case 5:benefitBonus=1.0;break;}};benefitPoints+=benefitBonus+userB+npb;};for(ne in userNegEffects){ne=ne.key;def strainNE=_source['side_effects'][ne];def userNE=userNegEffects[ne];negPoints=0;if(userNE==0||strainNE==0){negPoints=0;}else{negPoints=(-1*(userNE-strainNE)^2)/psa;};negEffectPoints+=negPoints;};def tp=effectPoints+negEffectPoints+benefitPoints;return(tp/psa)*100;"
                            }
                        }
                    ]
                }
            }
        }

    def parse_criteria_data(self, criteria):
        data = {}
        data_sum = 0

        if criteria and len(criteria) > 0 and criteria != 'skipped':
            for e in criteria:
                data_sum += e.get('value')
                data[e.get('name')] = e.get('value')

        return {
            'data': data,
            'sum': data_sum
        }

    def lookup_strain(self, query):
        method = self.METHODS.get('POST')
        url = '{base}{index}/{type}/_search'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('STRAIN'),
            type='name'
        )

        query = {
            "suggest": {
                "name_suggestion": {
                    "text": query,
                    "completion": {
                        "field": "name_suggest"
                    }
                }
            }
        }

        es_response = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_suggest_results(es_response)
        return results

    def _transform_suggest_results(self, es_response):
        suggests = es_response.get('suggest', {}).get('name_suggestion', {})
        total = 0
        payloads = []

        for s in suggests:
            options = s.get('options')
            if options:
                total = len(options)
                for o in options:
                    payloads.append(o.get('payload'))

        return {
            'total': total,
            'payloads': payloads
        }


"""
Groovy script unminified

Workflow:
    - use https://groovyconsole.appspot.com/ to validate script runs
    - minify via http://codebeautify.org/javaviewer (copy only part below comment below that is actual script)
    - paste minified version into script field in query_strain_srx_score

// TEMP for testing syntax
def effectSum = 20;
def benefitSum = 1;

def _source = [
    'effects': [
        'happy': 5,
        'relaxed': 4,
        'creative': 2,
        'talkative': 2,
        'energetic': 2,
        'sleepy': 5
    ],
    'side_effects': [
        'dry_mouth': 1
    ],
    'benefits': [
        'relieve_pain': 2
    ]
];

def userEffects = [
    'happy': 5,
    'relaxed': 5,
    'creative': 2,
    'talkative': 2,
    'energetic': 2,
    'sleepy': 5
];

def userBenefits = [
    //'relieve_pain': 4
];

def userNegEffects = [
    //'dry_mouth': 3
];


// actual script below here
//***********************************************************************

// points available
def psa = effectSum + benefitSum;

// calculate distance
def benefitPoints = 0;
def effectPoints = 0;
def negEffectPoints = 0;
def distLookup = [
    (-5): -1,
    (-4): -0.8,
    (-3): -0.51,
    (-2): -0.33,
    (-1): -0.14,
    (0): 0,
    (1): -0.01,
    (2): -0.01,
    (3): -0.01,
    (4): -0.01,
    (5): -0.01
];

// calc all effect points awarded
for (e in userEffects) {
    e = e.key;
    def strainE = _source['effects'][e];
    def userE = userEffects[e];
    def effectBonus = 0.0;

    dist = strainE - userE;
    npe = distLookup[dist] * userE;


    if (userE == strainE) {
        switch (strainE) {
            // 0-2 are +0 so ignore
            case 3:
                effectBonus = 0.3;
                break;
            case 4:
                effectBonus = 0.5;
                break;
            case 5:
                effectBonus = 1.0;
                break;
        }
    };

    effectPoints += effectBonus + userE + npe;
};

// calc all benefit points awarded
for (b in userBenefits) {
    b = b.key;
    def strainB = _source['benefits'][b];
    def userB = userBenefits[b];
    def benefitBonus = 0.0;

    dist = strainB - userB;
    npb = distLookup[dist] * userB;


    if (userB == strainB) {
        switch (strainB) {
            // 0-2 are +0 so ignore
            case 3:
                benefitBonus = 0.3;
                break;
            case 4:
                benefitBonus = 0.5;
                break;
            case 5:
                benefitBonus = 1.0;
                break;
        }
    };

    benefitPoints += benefitBonus + userB + npb;
};

for (ne in userNegEffects) {
    ne = ne.key;
    def strainNE = _source['side_effects'][ne];
    def userNE = userNegEffects[ne];
    negPoints = 0;

    if (userNE == 0 || strainNE == 0) {
        negPoints = 0;
    } else {
        negPoints = (-1 * (userNE - strainNE)^2) / psa;
    };

    negEffectPoints += negPoints;
};

//println 'effect';
//println effectPoints;

//println 'benefit';
//println benefitPoints;

//println 'neg';
//println negEffectPoints;

def tp = effectPoints + negEffectPoints + benefitPoints;
return (tp / psa) * 100;
"""
