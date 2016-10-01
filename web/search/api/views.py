import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
    print('asdasd')

    def get(self, request):
        print(request.data.get('page'))
        print(request.data.get('size'))
        # search_criteria = request.session.get('search_criteria')
        # search ElasticSearch paginated
        return Response({}, status=status.HTTP_200_OK)
