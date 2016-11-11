import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.search.api.serializers import SearchCriteriaSerializer, StrainReviewFormSerializer
from web.search.api.services import StrainDetailsService
from web.search.es_service import SearchElasticService
from web.search.models import Strain, StrainImage, Effect, StrainReview

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


class StrainLikeView(LoginRequiredMixin, APIView):
    def post(self, request):
        add_to_favorites = request.data.get('like')
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
        is_approved = False if review_text else True
        review = StrainReview(strain=strain, created_by=request.user,
                              rating=serializer.validated_data.get('rating'),
                              review=review_text, review_approved=is_approved)
        review.save()
        return Response({}, status=status.HTTP_200_OK)


class StrainDetailsView(LoginRequiredMixin, APIView):
    def get(self, request, strain_id):
        details = StrainDetailsService().build_strain_details(strain_id, request.user)
        return Response(details, status=status.HTTP_200_OK)


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
