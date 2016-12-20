import json

from web.es_service import BaseElasticService
from web.search import es_mappings


class BusinessLocationESService(BaseElasticService):
    def get_business_location_by_db_id(self, db_id):
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('BUSINESS_LOCATION'),
                                                    type=es_mappings.TYPES.get('business_location'))

        query = {"query": {"match": {"business_location_id": db_id}}}
        es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(query))
        return es_response

    def save_business_location(self, data, business_location_id):
        es_response = self.get_business_location_by_db_id(business_location_id)
        es_location = es_response.get('hits', {}).get('hits', [])

        if len(es_location) > 0:
            existing_source = es_location[0].get('_source')
            self.update_business_location_data(existing_source, data)
            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL,
                                                        index=self.URLS.get('BUSINESS_LOCATION'),
                                                        type=es_mappings.TYPES.get('business_location'),
                                                        es_id=es_location[0].get('_id'))
            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(existing_source))
        else:
            data['menu_items'] = []
            url = '{base}{index}/{type}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('BUSINESS_LOCATION'),
                                                type=es_mappings.TYPES.get('business_location'))
            es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(data))

        return es_response

    def update_business_location_data(self, existing_data, new_data):
        existing_data['location_name'] = new_data.get('location_name')
        existing_data['manager_name'] = new_data.get('manager_name')
        existing_data['location_email'] = new_data.get('location_email')
        existing_data['dispensary'] = new_data.get('dispensary')
        existing_data['delivery'] = new_data.get('delivery')
        existing_data['grow_house'] = new_data.get('grow_house')
        existing_data['delivery_radius'] = new_data.get('delivery_radius')
        existing_data['street1'] = new_data.get('street1')
        existing_data['city'] = new_data.get('city')
        existing_data['state'] = new_data.get('state')
        existing_data['zip_code'] = new_data.get('zip_code')
        existing_data['location'] = {
            "lat": new_data.get('lat') if new_data.get('lat') else 0,
            "lon": new_data.get('lng') if new_data.get('lng') else 0
        }
        existing_data['location_raw'] = new_data.get('location_raw')
        existing_data['phone'] = new_data.get('phone')
        existing_data['ext'] = new_data.get('ext')
        existing_data['removed_by_id'] = new_data.get('removed_by_id')
        existing_data['removed_date'] = new_data.get('removed_date')
        existing_data['created_date'] = new_data.get('created_date')
        existing_data['mon_open'] = new_data.get('mon_open')
        existing_data['mon_close'] = new_data.get('mon_close')
        existing_data['tue_open'] = new_data.get('tue_open')
        existing_data['tue_close'] = new_data.get('tue_close')
        existing_data['wed_open'] = new_data.get('wed_open')
        existing_data['wed_close'] = new_data.get('wed_close')
        existing_data['thu_open'] = new_data.get('thu_open')
        existing_data['thu_close'] = new_data.get('thu_close')
        existing_data['fri_open'] = new_data.get('fri_open')
        existing_data['fri_close'] = new_data.get('fri_close')
        existing_data['sat_open'] = new_data.get('sat_open')
        existing_data['sat_close'] = new_data.get('sat_close')
        existing_data['sun_open'] = new_data.get('sun_open')
        existing_data['sun_close'] = new_data.get('sun_close')

    def save_menu_item(self, data, menu_item_id, business_location_id):
        es_response = self.get_business_location_by_db_id(business_location_id)
        es_location = es_response.get('hits', {}).get('hits', [])

        if len(es_location) > 0:
            existing_source = es_location[0].get('_source')
            menu_items = existing_source.get('menu_items')
            exist = False

            for mi in menu_items:
                if mi.get('id') == menu_item_id:
                    mi['price_gram'] = data.get('price_gram')
                    mi['price_eighth'] = data.get('price_eighth')
                    mi['price_quarter'] = data.get('price_quarter')
                    mi['price_half'] = data.get('price_half')
                    mi['in_stock'] = data.get('in_stock')
                    mi['removed_date'] = data.get('removed_date')
                    exist = True

            if not exist:
                menu_items.append(data)

            existing_source['menu_items'] = menu_items

            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL,
                                                        index=self.URLS.get('BUSINESS_LOCATION'),
                                                        type=es_mappings.TYPES.get('business_location'),
                                                        es_id=es_location[0].get('_id'))

            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(existing_source))
            return es_response

        return None