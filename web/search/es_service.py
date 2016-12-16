import json
import logging
from datetime import datetime

from web.es_service import BaseElasticService
from web.search import es_mappings
from web.search.models import StrainImage, Strain
from web.system.models import SystemProperty

logger = logging.getLogger(__name__)


class SearchElasticService(BaseElasticService):
    srx_score_script_min = "def psa=effectSum+benefitSum;def benefitPoints=0;def effectPoints=0;def negEffectPoints=0;for(e in userEffects){e=e.key;def strainE=_source['effects'][e];def userE=userEffects[e];def effectBonus=0.0;dist=strainE-userE;if(dist>0){npe=-0.01;}else{npe=dist*0.2*userE;};if(userE==strainE){switch(strainE){case 3:effectBonus=0.3;break;case 4:effectBonus=0.5;break;case 5:effectBonus=1.0;break;}};effectPoints+=effectBonus+userE+npe;};for(b in userBenefits){b=b.key;def strainB=_source['benefits'][b];def userB=userBenefits[b];def benefitBonus=0.0;dist=strainB-userB;if(dist>0){npb=-0.01;}else{npb=dist*0.2*userB;};if(userB==strainB){switch(strainB){case 3:benefitBonus=0.3;break;case 4:benefitBonus=0.5;break;case 5:benefitBonus=1.0;break;}};benefitPoints+=benefitBonus+userB+npb;};for(ne in userNegEffects){ne=ne.key;def strainNE=_source['side_effects'][ne];def userNE=userNegEffects[ne];negPoints=0;if(userNE==0||strainNE==0){negPoints=0;}else{negPoints=(((userNE-strainNE)**2)*-1)/psa;};negEffectPoints+=negPoints;};def tp=effectPoints+negEffectPoints+benefitPoints;return(tp/psa)*100;"

    def _transform_strain_results(self, results, current_user=None, result_filter=None):
        """

        :param results:
        :return:
        """
        strains = results.get('hits', {}).get('hits', [])
        total = results.get('hits', {}).get('total', 0)
        processed_results = []

        strain_ratings = {}
        strain_rating_buckets = results.get('aggregations', {}).get('strain_rating', {}).get('buckets', [])
        for b in strain_rating_buckets:
            strain_ratings[b.get('key')] = b.get('child_rating').get('avg_rating').get('value')

        for s in strains:
            source = s.get('_source', {})
            db_strain = Strain.objects.get(pk=source.get('id'))
            rating = strain_ratings.get(source.get('id'))
            strain_image = StrainImage.objects.filter(strain=db_strain)[:1]
            srx_score = int(round(s.get('_score')))

            dispensaries = self.get_locations(source.get('id'), "dispensary", current_user, result_filter)
            dispensaries = self.transform_location_results(dispensaries, source.get('id'), result_filter, current_user)

            deliveries = self.get_locations(source.get('id'), "delivery", current_user, result_filter)
            deliveries = self.transform_location_results(deliveries, source.get('id'), result_filter, current_user)

            if result_filter == 'delivery' and len(deliveries) == 0:
                # means user is not in delivery radius of any delivery
                pass
            else:
                processed_results.append({
                    'id': source.get('id'),
                    'name': source.get('name'),
                    'strain_slug': source.get('strain_slug'),
                    'variety': source.get('variety'),
                    'category': source.get('category'),
                    'rating': "{0:.2f}".format(round(rating, 2)) if rating else 'Not Rated',
                    'image_url': strain_image[0].image.url if len(strain_image) > 0 else None,
                    'match_percentage': srx_score if srx_score <= 100 else 100,
                    'deliveries': deliveries,
                    'locations': dispensaries
                })

        response_data = {
            'list': processed_results,
            'total': total
        }

        return response_data

    def get_locations(self, strain_id=None, location_type=None, current_user=None, result_filter=None,
                      order_field="menu_items.price_gram", order_dir="asc"):

        method = self.METHODS.get('GET')
        url = '{0}{1}{2}'.format(self.BASE_ELASTIC_URL, self.URLS.get('BUSINESS_LOCATION'), '/_search')

        lat = None
        lon = None
        proximity = None

        if current_user:
            l = current_user.get_location()
            if l:
                lat = l.lat
                lon = l.lng

            if result_filter == 'local':
                proximity = current_user.proximity if current_user.proximity else 10

        if not proximity:
            proximity = SystemProperty.objects.get(name='max_delivery_radius')
            proximity = int(proximity.value)

        filter_query = {"geo_distance": {
            "distance": "{0}mi".format(proximity),
            "distance_type": "plane", "location": {"lat": lat, "lon": lon}
        }} if lat and lon else {}

        sort_query = [{order_field: {"order": order_dir}}]
        if lat and lon:
            sort_query.append({"_geo_distance": {
                "location": {"lat": lat, "lon": lon}, "order": "asc", "unit": "mi", "distance_type": "plane"
            }})

        menu_items_must_query = [{"missing": {"field": "menu_items.removed_date"}}]
        if strain_id:
            menu_items_must_query.append({"match": {"menu_items.strain_id": strain_id}})

        must_query = [{"nested": {"path": "menu_items", "query": {"bool": {"must": menu_items_must_query}}}}]
        if location_type:
            must_query.append({"match": {location_type: True}})

        query = {
            "query": {
                "bool": {
                    "must": must_query,
                    "filter": filter_query
                }
            },
            "sort": sort_query
        }

        return self._request(method, url, data=json.dumps(query))

    def transform_location_results(self, es_response, strain_id=None, result_filter=None, current_user=None):
        locations = es_response.get('hits', {}).get('hits', [])
        processed_results = []

        for l in locations:
            s = l.get('_source')
            sort = l.get('sort')
            distance = sort[1] if sort and len(sort) >= 2 else None

            if result_filter == 'delivery':
                delivery_radius = s.get('delivery_radius')
                if delivery_radius and delivery_radius >= distance:
                    self.add_location(processed_results, s, strain_id, distance)
            elif result_filter == 'local' and current_user:
                proximity = current_user.proximity if current_user.proximity else 10
                if distance <= proximity:
                    self.add_location(processed_results, s, strain_id, distance)
            else:
                self.add_location(processed_results, s, strain_id, distance)

        return processed_results

    def add_location(self, processed_results, s, strain_id, distance):
        menu_item_id = None
        in_stock = False
        price_gram = None
        price_half = None
        price_quarter = None
        price_eighth = None

        for mi in s.get('menu_items'):
            if int(mi.get('strain_id')) == int(strain_id):
                menu_item_id = mi.get('id')
                in_stock = mi.get('in_stock')
                price_gram = mi.get('price_gram')
                price_half = mi.get('price_half')
                price_quarter = mi.get('price_quarter')
                price_eighth = mi.get('price_eighth')

        processed_results.append({
            'business_id': s.get('business_id'), 'location_id': s.get('business_location_id'),
            'location_name': s.get('location_name'), 'distance': distance,
            'menu_item_id': menu_item_id, 'in_stock': in_stock,
            'price_gram': price_gram, 'price_half': price_half,
            'price_quarter': price_quarter, 'price_eighth': price_eighth,
            'open': self.is_open(s),
            'is_delivery': s.get('delivery'),
            'rating': 4.5  # TODO load here location rating
        })

    def is_open(self, location_json):
        days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
        now = datetime.now()
        current_day_index = int(now.strftime('%w'))  # 0 - Sunday, 6 - Saturday
        current_hour = int(now.strftime('%H'))

        location_o = location_json.get('{0}_open'.format(days[current_day_index]))
        location_c = location_json.get('{0}_close'.format(days[current_day_index]))
        if location_o and location_c:
            location_o = datetime.strptime(location_o, '%I:%M %p')
            location_c = datetime.strptime(location_c, '%I:%M %p')
            return int(datetime.strftime(location_o, '%H')) < current_hour < int(datetime.strftime(location_c, '%H'))

        return False

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

    def query_user_review_srx_score(self, criteria, strain_id=None, user_id=None):
        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('USER_RATINGS'),
                                                    type=es_mappings.TYPES.get('strain_rating'))

        query = self.build_srx_score_user_review_es_query(criteria, strain_id, user_id)
        es_response = self._request(method, url, data=json.dumps(query))

        # remove extra info returned by ES and do any other necessary transforms
        results = self.transform_user_review_results(es_response)
        return results

    def build_srx_score_user_review_es_query(self, criteria, strain_id, user_id):
        effects_data = self.parse_criteria_data(criteria.get('effects'))
        benefits_data = self.parse_criteria_data(criteria.get('benefits'))
        side_effects_data = self.parse_criteria_data(criteria.get('side_effects'))

        strain_filter = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"strain_id": strain_id}},
                        {"term": {"user_id": user_id}}
                    ],
                    "filter": {
                        "missing": {"field": "removed_date"}
                    }
                }
            }
        }

        return {
            "query": {
                "function_score": {
                    "query": strain_filter,
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
                                "script": self.srx_score_script_min
                            }
                        }
                    ]
                }
            }
        }

    def transform_user_review_results(self, results):
        strains = results.get('hits', {}).get('hits', [])
        score = int(round(strains[0].get('_score'))) if len(strains) > 0 else 'n/a'

        if score != 'n/a':
            return score if score <= 100 else 100
        else:
            return score

    def query_strain_srx_score(self, criteria, size=50, start_from=0, strain_id=None, current_user=None,
                               result_filter=None):
        """
            Return strains ranked by SRX score
        """
        if start_from is None:
            start_from = 0

        strain_ids = []
        if strain_id:
            strain_ids.append(strain_id)

        proximity = SystemProperty.objects.get(name='max_delivery_radius')
        proximity = int(proximity.value)

        method = self.METHODS.get('GET')
        url = '{base}{index}/{type}/_search?size={size}&from={start_from}'.format(
            base=self.BASE_ELASTIC_URL,
            index=self.URLS.get('STRAIN'),
            type=es_mappings.TYPES.get('strain'),
            size=size,
            start_from=start_from
        )

        if result_filter == 'all':
            query = self.build_srx_score_es_query(criteria, strain_ids)
        elif result_filter == 'local':
            strain_ids = self.get_strain_ids_available_locally(current_user)
            query = self.build_srx_score_es_query(criteria, strain_ids)
        elif result_filter == 'delivery':
            strain_ids = self.get_strain_ids_available_locally(current_user, True, deliver_max=proximity)
            query = self.build_srx_score_es_query(criteria, strain_ids)
        else:
            query = self.build_srx_score_es_query(criteria, strain_ids)

        es_response = self._request(method, url, data=json.dumps(query))
        results = self._transform_strain_results(es_response, current_user, result_filter)
        return results

    def build_srx_score_es_query(self, criteria, strain_ids):
        criteria_strain_types = self.parse_criteria_strains(criteria.get('strain_types'))
        effects_data = self.parse_criteria_data(criteria.get('effects'))
        benefits_data = self.parse_criteria_data(criteria.get('benefits'))
        side_effects_data = self.parse_criteria_data(criteria.get('side_effects'))

        strain_variety_filter = {
            "filtered": {
                "filter": {
                    "terms": {
                        "variety": criteria_strain_types
                    }
                }
            }
        }

        strain_id_filter = {
            "filtered": {
                "filter": {
                    "terms": {
                        "id": strain_ids
                    }
                }
            }
        }

        match_all_varieties = {
            "match_all": {}
        }

        # if user skipped picking variety match all strains
        strain_filter = strain_variety_filter if criteria_strain_types else match_all_varieties
        strain_filter = strain_id_filter if len(strain_ids) > 0 else strain_filter

        strain_aggs = {
            "strain_rating": {
                "terms": {
                    "field": "id",
                    "order": {
                        "srx_score": "desc"
                    }
                },
                "aggs": {
                    "child_rating": {
                        "children": {
                            "type": "strain_review"
                        },
                        "aggs": {
                            "avg_rating": {
                                "avg": {
                                    "field": "rating"
                                }
                            }
                        }
                    },
                    "srx_score": {
                        "max": {
                            "script": "_score"
                        }
                    }
                }
            }
        }

        return {
            "aggs": strain_aggs,
            "query": {
                "function_score": {
                    "query": strain_filter,
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
                                "script": self.srx_score_script_min
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

    def parse_criteria_strains(self, criteria):
        if criteria == 'skipped':
            strains = False
        else:
            strains = [k.lower() for k, v in criteria.items() if v]

        return strains

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

    def get_strain_ids_available_locally(self, current_user, only_deliveries=False, deliver_max=None):
        strain_ids = []

        if current_user:
            l = current_user.get_location()
            p = deliver_max if deliver_max else current_user.proximity

            if l and l.lat and l.lng:
                if not only_deliveries:
                    dispensaries = self.get_locations(location_type="dispensary", current_user=current_user)
                    strain_ids_id_dispensaries = self.get_strain_ids_from_locations(dispensaries)
                    for i in strain_ids_id_dispensaries:
                        if i not in strain_ids:
                            strain_ids.append(i)

                deliveries = self.get_locations(location_type="delivery", current_user=current_user)
                strain_ids_id_deliveries = self.get_strain_ids_from_locations(deliveries)
                for i in strain_ids_id_deliveries:
                    if i not in strain_ids:
                        strain_ids.append(i)

        return strain_ids

    def get_strain_ids_from_locations(self, es_locations_response):
        locations = es_locations_response.get('hits', {}).get('hits', [])
        ids = []
        for l in locations:
            s = l.get('_source')
            for mi in s.get('menu_items'):
                if not mi.get('removed_date'):
                    ids.append(mi.get('strain_id'))
        return ids


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
        'happy': 4.5,
        'relaxed': 4.0,
        'creative': 2.23,
        'talkative': 2.123,
        'energetic': 1.564,
        'sleepy': 3.23
    ],
    'side_effects': [
        'dry_mouth': 7.4
    ],
    'benefits': [
        'relieve_pain': 2.0
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
    'relieve_pain': 4
];

def userNegEffects = [
    'dry_mouth': 3
];


// actual script below here
//***********************************************************************

// points available
def psa = effectSum + benefitSum;

// calculate distance
def benefitPoints = 0;
def effectPoints = 0;
def negEffectPoints = 0;

// calc all effect points awarded
for (e in userEffects) {
    e = e.key;
    def strainE = _source['effects'][e];
    def userE = userEffects[e];
    def effectBonus = 0.0;

    dist = strainE - userE;
    if (dist > 0) {
        npe = -0.01;
    } else {
        npe = dist * 0.2 * userE;
    };

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
    if (dist > 0) {
        npb = -0.01;
    } else {
        npb = dist * 0.2 * userB;
    };

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
        negPoints = (((userNE - strainNE)**2) * -1) / psa;
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
return (tp / psa) * 100;​
"""
