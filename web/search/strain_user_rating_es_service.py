import json

from web.es_service import BaseElasticService
from web.search import es_mappings


class StrainUserRatingESService(BaseElasticService):
    def get_user_review(self, db_strain_id, db_user_id):
        url = '{base}{index}/{type}/_search'.format(base=self.BASE_ELASTIC_URL,
                                                    index=self.URLS.get('USER_RATINGS'),
                                                    type=es_mappings.TYPES.get('strain_rating'))
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"strain_id": db_strain_id}},
                        {"term": {"user_id": db_user_id}}
                    ],
                    "filter": {
                        "missing": {"field": "removed_date"}
                    }
                }
            }
        }

        es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps(query))
        return es_response

    def save_strain_review(self, updated_review, db_strain_id, db_user_id):
        es_response = self.get_user_review(db_strain_id, db_user_id)
        es_reviews = es_response.get('hits', {}).get('hits', [])

        if len(es_reviews) > 0:
            review_es_id = es_reviews[0].get('_id')
            review = es_reviews[0].get('_source')

            review["effects"] = updated_review.effects,
            review["effects_changed"] = updated_review.effects_changed,
            review["benefits"] = updated_review.benefits,
            review["benefits_changed"] = updated_review.benefits_changed,
            review["side_effects"] = updated_review.side_effects,
            review["side_effects_changed"] = updated_review.side_effects_changed,
            review["status"] = updated_review.status,
            review["removed_date"] = updated_review.removed_date.isoformat() if updated_review.removed_date else None

            url = '{base}{index}/{type}/{es_id}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('USER_RATINGS'),
                                                        type=es_mappings.TYPES.get('strain_rating'),
                                                        es_id=review_es_id)
            es_response = self._request(self.METHODS.get('PUT'), url, data=json.dumps(review))
        else:
            url = '{base}{index}/{type}'.format(base=self.BASE_ELASTIC_URL, index=self.URLS.get('USER_RATINGS'),
                                                type=es_mappings.TYPES.get('strain_rating'))
            es_response = self._request(self.METHODS.get('POST'), url, data=json.dumps({
                "strain_id": db_strain_id,
                "user_id": db_user_id,
                "effects": updated_review.effects,
                "effects_changed": updated_review.effects_changed,
                "benefits": updated_review.benefits,
                "benefits_changed": updated_review.benefits_changed,
                "side_effects": updated_review.side_effects,
                "side_effects_changed": updated_review.side_effects_changed,
                "status": updated_review.status,
                "removed_date": updated_review.removed_date.isoformat() if updated_review.removed_date else None
            }))

        return es_response
