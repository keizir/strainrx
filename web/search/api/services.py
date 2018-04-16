from web.search.api.serializers import StrainDetailSerializer, StrainRatingSerializer
from web.search.es_service import SearchElasticService
from web.search.models import UserSearch, Strain, StrainImage, StrainReview, StrainRating, UserFavoriteStrain
from web.search.services import build_strain_rating


class StrainDetailsService:
    def build_strain_details(self, strain_id, current_user=None):
        strain = Strain.objects.get(pk=strain_id)
        image = StrainImage.objects.filter(strain=strain, is_approved=True).first()
        strain_origins = self.get_strain_origins(strain)
        rating = build_strain_rating(strain)
        reviews = self.get_strain_reviews(strain)

        if current_user:
            strain_srx_score = self.calculate_srx_score(strain, current_user)
            strain_review = StrainRating.objects.filter(strain=strain, created_by=current_user, removed_date=None)
            favorite = UserFavoriteStrain.objects.filter(strain=strain, created_by=current_user).exists()
            is_rated = StrainReview.objects.filter(strain=strain, created_by=current_user).exists()
            user_criteria = UserSearch.objects.user_criteria(current_user)
            if user_criteria:
                user_criteria = user_criteria.to_search_criteria()
        else:
            strain_srx_score = 0
            strain_review = []
            favorite = None
            is_rated = None
            user_criteria = None

        return {
            'strain': StrainDetailSerializer(strain).data,
            'strain_image': image.image.url if image and image.image else None,
            'strain_origins': strain_origins,
            'strain_rating': rating,
            'user_strain_review': StrainRatingSerializer(strain_review[0]).data if len(strain_review) > 0 else None,
            'user_criteria': user_criteria,
            'strain_reviews': reviews,
            'strain_srx_score': strain_srx_score,
            'favorite': favorite,
            'is_rated': is_rated
        }

    @staticmethod
    def get_strain_origins(current_strain):
        strain_origins = []
        for o in current_strain.origins.all()[:5]:
            strain_origins.append(StrainDetailSerializer(o).data)
        return strain_origins

    @staticmethod
    def get_also_like_strains(current_strain, current_user=None):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        also_like_strains = []

        if latest_user_search:
            data = SearchElasticService().query_strain_srx_score(latest_user_search.to_search_criteria(), 2000, 0,
                                                                 include_locations=False, is_similar=True,
                                                                 similar_strain_id=current_strain.id)
            for index, s in enumerate(data.get('list')):
                also_like_strains.append(s)

        if len(also_like_strains) == 0:
            criteria = current_strain.to_search_criteria()
            if len(criteria['effects']) > 0 or len(criteria['benefits']) > 0 or len(criteria['side_effects']) > 0:
                criteria['strain_types'] = 'skipped'
                data = SearchElasticService().query_strain_srx_score(criteria, 2000, 0,
                                                                     include_locations=False, is_similar=True,
                                                                     similar_strain_id=current_strain.id)
                for s in data.get('list'):
                    also_like_strains.append(s)

        return also_like_strains

    @staticmethod
    def calculate_srx_score(current_strain, current_user):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        if latest_user_search:
            if StrainRating.objects.filter(strain=current_strain, created_by=current_user,
                                           removed_date=None).exists():
                score = SearchElasticService().query_user_review_srx_score(latest_user_search.to_search_criteria(),
                                                                           strain_id=current_strain.id,
                                                                           user_id=current_user.id)
                return score
            else:
                data = SearchElasticService().query_strain_srx_score(
                    latest_user_search.to_search_criteria(), strain_ids=[current_strain.id], include_locations=False)
                strain = data.get('list')[0] if len(data.get('list')) > 0 else {'match_percentage': 0}
                return strain.get('match_percentage')

        return 0

    @staticmethod
    def calculate_srx_scores(strain_ids, current_user):
        latest_user_search = UserSearch.objects.user_criteria(current_user)

        if latest_user_search:
            data = SearchElasticService().query_strain_srx_score(latest_user_search.to_search_criteria(),
                                                                 strain_ids=strain_ids)
            scores = {}
            strains = data.get('list')

            for s in strains:
                scores[s.get('id')] = s.get('match_percentage')

            return scores

        return []

    def get_strain_reviews(self, current_strain):
        reviews_raw = StrainReview.objects.filter(strain=current_strain,
                                                  review_approved=True).order_by('-created_date')[:3]
        reviews = []
        for r in reviews_raw:
            reviews.append(self.build_review(r))
        return reviews

    def get_all_approved_strain_reviews(self, strain_id):
        reviews_raw = StrainReview.objects.filter(strain__id=strain_id,
                                                  review_approved=True).order_by('-created_date')
        reviews = []
        for r in reviews_raw:
            reviews.append(self.build_review(r))
        return reviews

    @staticmethod
    def build_review(review):
        created_by = review.created_by
        display_user_name = '{0} {1}.'.format(created_by.first_name, created_by.last_name[0]) \
            if created_by.first_name and created_by.last_name \
            else created_by.email.split('@')[0]

        return {
            'id': review.id,
            'rating': review.rating,
            'review': review.review,
            'created_date': review.created_date,
            'created_by_name': display_user_name,
            'created_by_image': created_by.image.url if created_by.image and created_by.image.url else None
        }

    @staticmethod
    def build_strain_locations(strain_id, current_user, order_field=None, order_dir=None, location_type=None):
        service = SearchElasticService()
        es_response = service.get_locations(strain_id=strain_id, current_user=current_user,
                                            order_field=order_field, order_dir=order_dir, location_type=location_type,
                                            size=6, only_active=True)

        locations = service.transform_location_results(es_response, strain_id=strain_id)
        return {'locations': locations}
