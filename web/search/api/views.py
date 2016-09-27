import logging
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class StrainSearchWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

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

        print(str(request.session['search_criteria']))

        return Response({}, status=status.HTTP_200_OK)

    def process_step_2(self, request):
        return Response({}, status=status.HTTP_200_OK)

    def process_step_3(self, request):
        return Response({}, status=status.HTTP_200_OK)

    def process_step_4(self, request):
        return Response({}, status=status.HTTP_200_OK)
