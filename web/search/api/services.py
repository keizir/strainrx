from web.search.api.serializers import StrainDetailSerializer, UserStrainReviewSerializer
from web.search.es_service import SearchElasticService
from web.search.models import UserSearch, Strain, StrainImage, StrainReview, UserStrainReview
from web.search.services import build_strain_rating


class StrainDetailsService:
    def build_strain_details(self, strain_id, current_user):
        strain = Strain.objects.get(pk=strain_id)
        image = StrainImage.objects.filter(strain=strain)[:1]

        strain_origins = self.get_strain_origins(strain)
        also_like_strains = self.get_also_like_strains(strain, current_user)
        dispensaries = self.get_dispensaries()
        rating = build_strain_rating(strain)
        strain_srx_score = self.calculate_srx_score(strain, current_user)
        reviews = self.get_strain_reviews(strain)

        effects_review = UserStrainReview.objects.filter(strain=strain, effect_type='effects',
                                                         created_by=current_user, removed_date=None)
        benefits_review = UserStrainReview.objects.filter(strain=strain, effect_type='benefits',
                                                          created_by=current_user, removed_date=None)
        side_effects_review = UserStrainReview.objects.filter(strain=strain, effect_type='side_effects',
                                                              created_by=current_user, removed_date=None)

        return {
            'strain': StrainDetailSerializer(strain).data,
            'strain_image': image[0].image.url if image else None,
            'strain_origins': strain_origins,
            'also_like_strains': also_like_strains,
            'strain_rating': rating,

            'strain_effects_review': UserStrainReviewSerializer(effects_review[0]).data if len(
                effects_review) > 0 else None,

            'strain_benefits_review': UserStrainReviewSerializer(benefits_review[0]).data if len(
                benefits_review) > 0 else None,

            'strain_side_effects_review': UserStrainReviewSerializer(side_effects_review[0]).data if len(
                side_effects_review) > 0 else None,

            'strain_reviews': reviews,
            'strain_srx_score': strain_srx_score,
            'favorite': True,  # TODO check user's favorites
            'dispensaries': dispensaries,
            'is_rated': StrainReview.objects.filter(strain=strain, created_by=current_user).exists()
        }

    @staticmethod
    def get_strain_origins(current_strain):
        strain_origins = []
        for o in current_strain.origins.all()[:5]:
            strain_origins.append(StrainDetailSerializer(o).data)
        return strain_origins

    @staticmethod
    def get_also_like_strains(current_strain, current_user):
        latest_user_search = UserSearch.objects.filter(user=current_user).order_by('-last_modified_date')[:1]
        also_like_strains = []

        if latest_user_search and len(latest_user_search) > 0:
            data = SearchElasticService().query_strain_srx_score(latest_user_search[0].to_search_criteria(), 100, 0)
            start_index = 0
            initial = 0
            for index, s in enumerate(data.get('list')):
                if s.get('id') == current_strain.id:
                    start_index = index + 1
                    initial = index + 1

                if index + 1 != start_index and 0 < start_index < initial + 5:
                    also_like_strains.append(s)
                    start_index += 1

        if len(also_like_strains) == 0:
            search_criteria = current_strain.to_search_criteria()
            search_criteria['strain_types'] = 'skipped'
            data = SearchElasticService().query_strain_srx_score(search_criteria, 5, 0)
            for s in data.get('list'):
                also_like_strains.append(s)

        return also_like_strains

    @staticmethod
    def get_dispensaries():  # TODO retrieve real dispensaries
        dispensaries = []
        for num in range(0, 5):
            dispensaries.append({
                'id': num,
                'name': 'The Green Shop',
                'rating': 4.6,
                'distance': 1.3,
                'price': {
                    'gram': 100.00,
                    'eight': 20.00,
                    'quarter': 30.00,
                    'half': 54.98
                }
            })
        return dispensaries

    @staticmethod
    def calculate_srx_score(current_strain, current_user):
        latest_user_search = UserSearch.objects.filter(user=current_user).order_by('-last_modified_date')[:1]

        if latest_user_search and len(latest_user_search) > 0:
            data = SearchElasticService().query_strain_srx_score(latest_user_search[0].to_search_criteria(),
                                                                 strain_id=current_strain.id)
            strain = data.get('list')[0]
            return strain.get('match_percentage')

        return 0

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
        display_user_name = '{0} {1}'.format(review.created_by.first_name, review.created_by.last_name) \
            if review.created_by.first_name and review.created_by.last_name \
            else review.created_by.email.split('@')[0]

        return {
            'id': review.id,
            'rating': review.rating,
            'review': review.review,
            'created_date': review.created_date,
            'created_by_name': display_user_name,
            'created_by_image': None  # TODO implement UserImage
        }
