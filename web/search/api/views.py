import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.search.api.serializers import SearchCriteriaSerializer, StrainReviewFormSerializer
from web.search.api.services import StrainDetailsService
from web.search.es_service import SearchElasticService
from web.search.models import Strain, StrainImage, Effect, StrainReview, UserStrainReview
from web.system.models import SystemProperty
from web.search.models import Strain, StrainImage, Effect, StrainReview, UserStrainReview, UserFavoriteStrain

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class StrainSearchWizardView(LoginRequiredMixin, APIView):
    def post(self, request):
        criteria = SearchCriteriaSerializer(data=request.data.get('search_criteria'))
        criteria.is_valid()

        step_1_data = criteria.validated_data.get('step1')
        step_2_data = criteria.validated_data.get('step2')
        step_3_data = criteria.validated_data.get('step3')
        step_4_data = criteria.validated_data.get('step4')

        types = 'skipped' if step_1_data.get('skipped') else step_1_data
        effects = 'skipped' if step_2_data.get('skipped') else step_2_data.get('effects')
        benefits = 'skipped' if step_3_data.get('skipped') else step_3_data.get('effects')
        side_effects = 'skipped' if step_4_data.get('skipped') else step_4_data.get('effects')

        request.session['search_criteria'] = {
            'strain_types': types,
            'effects': effects,
            'benefits': benefits,
            'side_effects': side_effects
        }

        return Response({}, status=status.HTTP_200_OK)


class StrainSearchResultsView(LoginRequiredMixin, APIView):
    def get(self, request):
        page = request.GET.get('page')
        size = request.GET.get('size')
        start_from = (int(page) - 1) * int(size)

        search_criteria = request.session.get('search_criteria')

        if search_criteria:
            data = SearchElasticService().query_strain_srx_score(search_criteria, size, start_from)
            result_list = data.get('list')
            return Response({
                'search_results': result_list,
                'search_results_total': data.get('total')
            }, status=status.HTTP_200_OK)

        return Response({
            "error": "Cannot determine a search criteria."
        }, status=status.HTTP_400_BAD_REQUEST)


class StrainFavoriteView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        add_to_favorites = request.data.get('like')
        favorite_strain = UserFavoriteStrain.objects.filter(strain__id=strain_id, created_by=request.user)

        if add_to_favorites and len(favorite_strain) == 0:
            favorite_strain = UserFavoriteStrain(
                strain=Strain.objects.get(id=strain_id),
                created_by=request.user
            )
            favorite_strain.save()
        elif len(favorite_strain) > 0:
            favorite_strain[0].delete()

        return Response({}, status=status.HTTP_200_OK)


class StrainLookupView(LoginRequiredMixin, APIView):
    def get(self, request):
        query = request.GET.get('q')
        result = SearchElasticService().lookup_strain(query)
        return Response({
            'total': result.get('total'),
            'payloads': result.get('payloads')
        }, status=status.HTTP_200_OK)


class StrainUploadImageView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        file = request.FILES.get('file')
        strain = Strain.objects.get(pk=strain_id)

        image = StrainImage()
        image.image = file
        image.strain = strain
        image.created_by = request.user
        image.save()

        return Response({}, status=status.HTTP_200_OK)


class StrainRateView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        strain = Strain.objects.get(pk=strain_id)
        serializer = StrainReviewFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review_text = serializer.validated_data.get('review')
        is_approved = False if review_text and len(review_text) > 0 else True
        review = StrainReview(strain=strain, created_by=request.user,
                              rating=serializer.validated_data.get('rating'),
                              review=review_text, review_approved=is_approved)
        review.save()
        return Response({}, status=status.HTTP_200_OK)


class StrainDetailsView(LoginRequiredMixin, APIView):
    def get(self, request, strain_id):
        details = StrainDetailsService().build_strain_details(strain_id, request.user)
        return Response(details, status=status.HTTP_200_OK)


class StrainReviewsView(LoginRequiredMixin, APIView):
    def get(self, request, strain_id):
        reviews = StrainDetailsService().get_all_approved_strain_reviews(strain_id)
        return Response({'reviews': reviews}, status=status.HTTP_200_OK)


class StrainUserReviewsView(LoginRequiredMixin, APIView):
    def post(self, request, strain_id):
        data = request.data
        effect_type = data.get('type')
        effects = data.get('effects')
        strain = Strain.objects.get(id=strain_id)
        sender_ip = get_client_ip(request)

        if 'positive-effects' == effect_type:
            if not UserStrainReview.objects.filter(strain=strain, effect_type='effects',
                                                   created_by=request.user, removed_date=None).exists():
                review = UserStrainReview(strain=strain, created_by=request.user, created_by_ip=sender_ip,
                                          effect_type='effects')
                review.effects = self.build_effects_object(effects, strain.effects)
                review.save()
                self.recalculate_global_effects(request, 'effects', strain)

        if 'medical-benefits' == effect_type:
            if not UserStrainReview.objects.filter(strain=strain, effect_type='benefits',
                                                   created_by=request.user, removed_date=None).exists():
                review = UserStrainReview(strain=strain, created_by=request.user, created_by_ip=sender_ip,
                                          effect_type='benefits')
                review.effects = self.build_effects_object(effects, strain.benefits)
                review.save()
                self.recalculate_global_effects(request, 'benefits', strain)

        if 'negative-effects' == effect_type:
            if not UserStrainReview.objects.filter(strain=strain, effect_type='side_effects',
                                                   created_by=request.user, removed_date=None).exists():
                review = UserStrainReview(strain=strain, created_by=request.user, created_by_ip=sender_ip,
                                          effect_type='side_effects')
                review.effects = self.build_effects_object(effects, strain.side_effects)
                review.save()
                self.recalculate_global_effects(request, 'side_effects', strain)

        return Response({}, status=status.HTTP_200_OK)

    def build_effects_object(self, effects, strain_default_effects):
        for default_e in strain_default_effects:
            strain_default_effects[default_e] = 0

        effects_to_persist = strain_default_effects
        for e in effects:
            effects_to_persist[e.get('name')] = e.get('value')
        return effects_to_persist

    def recalculate_global_effects(self, request, effect_type, strain):
        try:
            recalculate_size = int(SystemProperty.objects.get(name='review_recalculation_size').value)
        except SystemProperty.DoesNotExist:
            recalculate_size = 10

        reviews = UserStrainReview.objects.filter(strain=strain, effect_type=effect_type,
                                                  status='pending', removed_date=None)

        # First check if there are "recalculate_size" new reviews
        if len(reviews) == recalculate_size:
            sender_ip = get_client_ip(request)

            for r in reviews:
                r.status = 'processed'
                r.last_modified_ip = sender_ip
                r.last_modified_by = request.user
                r.last_modified_date = datetime.now()
                r.save()

            if effect_type == 'effects':
                strain.effects = self.calculate_new_global_values(strain, 'effects')
                strain.save()

            if effect_type == 'benefits':
                strain.benefits = self.calculate_new_global_values(strain, 'benefits')
                strain.save()

            if effect_type == 'side_effects':
                strain.side_effects = self.calculate_new_global_values(strain, 'side_effects')
                strain.save()

    def calculate_new_global_values(self, strain, effect_type):
        # Recalculate Global scores for each review in the system that wasn't removed
        reviews = UserStrainReview.objects.filter(strain=strain, effect_type=effect_type, removed_date=None)
        total_strain_effects = {}
        for r in reviews:
            for effect_name in r.effects:
                if total_strain_effects.get(effect_name):
                    total_strain_effects[effect_name] += r.effects[effect_name]
                else:
                    total_strain_effects[effect_name] = r.effects[effect_name]

        for effect_name in total_strain_effects:
            total_strain_effects[effect_name] /= len(reviews)

        return total_strain_effects

    def delete(self, request, strain_id):
        effect_type = request.data.get('effect_type')
        sender_ip = get_client_ip(request)
        strain = Strain.objects.get(id=strain_id)
        review = UserStrainReview.objects.get(strain=strain, effect_type=effect_type,
                                              created_by=request.user, removed_date=None)

        review.removed_date = datetime.now()
        review.last_modified_ip = sender_ip
        review.last_modified_by = request.user
        review.last_modified_date = datetime.now()
        review.save()

        if review.status == 'processed':
            if effect_type == 'effects':
                strain.effects = self.calculate_new_global_values(strain, 'effects')
                strain.save()

            if effect_type == 'benefits':
                strain.benefits = self.calculate_new_global_values(strain, 'benefits')
                strain.save()

            if effect_type == 'side_effects':
                strain.side_effects = self.calculate_new_global_values(strain, 'side_effects')
                strain.save()

        return Response({}, status=status.HTTP_200_OK)


def get_client_ip(request):
    return request.META.get('X-Real-IP')


class StrainEffectView(LoginRequiredMixin, APIView):
    def get(self, request, effect_type):
        effects_raw = Effect.objects.filter(effect_type=effect_type)
        effects = []

        for e in effects_raw:
            effects.append({
                'data_name': e.data_name,
                'display_name': e.display_name
            })

        return Response(effects, status=status.HTTP_200_OK)
