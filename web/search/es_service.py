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

        method = self.METHODS.get('GET')
        url = '{base}{index}{type}/_search?size={size}&from={start_from}'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('STRAIN'),
            type='flower',
            size=size,
            start_from=start_from
        )

        query = {
            "query": {
                "function_score": {
                    "query": {
                        "match_all": {}
                    },
                    "functions": [
                        {
                            "script_score": {
                                "params": {
                                    "effectSum": 20, # TODO sum effect ratings from user criteria
                                    "benefitSum": 3, # TODO sum benefit ratings from user criteria
                                    "userEffects": { # TODO use actual user ratings
                                        "happy": 5,
                                        "relaxed": 4,
                                        "creative": 2,
                                        "talkative": 2,
                                        "energetic": 2,
                                        "sleepy": 5
                                    },
                                    "userBenefits": { # TODO use actual user ratings
                                        "reduce_fatigue": 3
                                    },
                                    "userNegEffects": { # TODO use actual user ratings
                                        "dry_eyes": 6
                                    }
                                },
                                "script": "def psa=effectSum+benefitSum;def benefitPoints=0;def effectPoints=0;def negEffectPoints=0;def distLookup=[(-5):-1,(-4):-0.8,(-3):-0.51,(-2):-0.33,(-1):-0.14,(0):0,(1):-0.01,(2):-0.01,(3):-0.01,(4):-0.01,(5):-0.01];for(e in userEffects){e=e.key;def strainE=_source['effects'][e];def userE=userEffects[e];def effectBonus=0.0;dist=strainE-userE;npe=distLookup[dist]*userE;if(userE==strainE){switch(strainE){case 3:effectBonus=0.3;break;case 4:effectBonus=0.5;break;case 5:effectBonus=1.0;break;}};effectPoints+=effectBonus+userE+npe;};for(b in userBenefits){b=b.key;def strainB=_source['benefits'][b];def userB=userBenefits[b];def benefitBonus=0.0;dist=strainB-userB;npb=distLookup[dist]*userB;if(userB==strainB){switch(strainB){case 3:benefitBonus=0.3;break;case 4:benefitBonus=0.5;break;case 5:benefitBonus=1.0;break;}};benefitPoints+=benefitBonus+userB+npb;};for(ne in userNegEffects){ne=ne.key;def strainNE=_source['side_effects'][ne];def userNE=userNegEffects[ne];negPoints=0;if(userNE==0||strainNE==0){negPoints=0;}else{negPoints=(-1*(userNE-strainNE)^2)/psa;};negEffectPoints+=negPoints;};def tp=effectPoints+negEffectPoints+benefitPoints;return(tp/psa)*100;"
                            }
                        }
                    ]
                }
            }
        }

        q = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self._transform_strain_results(q)

        return results




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
