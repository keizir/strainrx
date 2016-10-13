import logging
from random import uniform

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.search.models import Strain, StrainImage

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class StrainSearchWizardView(LoginRequiredMixin, APIView):
    def post(self, request):
        step = request.data.get('step')

        if step is not None:
            return self.process_step(request, step)

        return bad_request('Invalid step number')

    def process_step(self, request, step):
        if step == 1:
            return self.process_step_1(request)

        if step == 2:
            return self.process_step_2(request)

        if step == 3:
            return self.process_step_3(request)

        if step == 4:
            return self.process_step_4(request)

    def process_step_1(self, request):
        data = request.data

        if data.get('skipped'):
            types = 'skipped'
        else:
            types = {'sativa': data.get('sativa'), 'hybrid': data.get('hybrid'), 'indica': data.get('indica')}

        request.session['search_criteria'] = {'strain_types': types}
        return Response({}, status=status.HTTP_200_OK)

    def process_step_2(self, request):
        data = request.data

        if data.get('skipped'):
            effects = 'skipped'
        else:
            effects = data.get('effects')

        search_criteria = request.session.get('search_criteria')
        search_criteria['effects'] = effects
        request.session['search_criteria'] = search_criteria
        return Response({}, status=status.HTTP_200_OK)

    def process_step_3(self, request):
        data = request.data

        if data.get('skipped'):
            benefits = 'skipped'
        else:
            benefits = data.get('benefits')

        search_criteria = request.session.get('search_criteria')
        search_criteria['benefits'] = benefits
        request.session['search_criteria'] = search_criteria
        return Response({}, status=status.HTTP_200_OK)

    def process_step_4(self, request):
        data = request.data

        if data.get('skipped'):
            side_effects = 'skipped'
        else:
            side_effects = data.get('sideEffects')

        search_criteria = request.session.get('search_criteria')
        search_criteria['side_effects'] = side_effects
        request.session['search_criteria'] = search_criteria
        return Response({}, status=status.HTTP_200_OK)


class StrainSearchResultsView(LoginRequiredMixin, APIView):
    def get(self, request):
        page = request.GET.get('page')
        size = request.GET.get('size')

        dummy_response = list()  # TODO remove this later - START

        for num in range(0, 8):
            dummy_response.append(
                {
                    'name': 'Blue Dream' if num % 2 == 0 else 'East Coast Sour Diesel',
                    'type': 'Sativa',
                    'rating': "{0:.2f}".format(5 * uniform(0.3, 1)),
                    'image': 'image_location.png',
                    'match_percentage': "{0:.2f}".format(100 * uniform(0.3, 1)),
                    'delivery_addresses': [
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
                }
            )

        dummy_response.sort(key=lambda entry: entry.get('match_percentage'), reverse=True)
        # TODO remove this later - END

        # search ElasticSearch paginated
        return Response({
            'search_results': dummy_response,
            'search_results_total': 24
        }, status=status.HTTP_200_OK)


class StrainLikeView(LoginRequiredMixin, APIView):
    def post(self, request):
        add_to_favorites = request.data.get('like')
        return Response({}, status=status.HTTP_200_OK)


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
