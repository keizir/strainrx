# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.businesses.api.serializers import BusinessSignUpSerializer
from web.businesses.api.services import BusinessSignUpService
from web.businesses.emails import EmailService
from web.businesses.models import Business
from web.businesses.serializers import BusinessSerializer

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class BusinessSignUpWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = BusinessSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            business = BusinessSignUpService().enroll_new_business(data=serializer.validated_data)
        except ValidationError as e:
            return bad_request(e.message)

        try:
            EmailService().send_confirmation_email(business.created_by)
        except Exception:
            logger.exception('Cannot send an email to {0}'.format(business.created_by.email))

        authenticated = authenticate(username=business.created_by.email, password=serializer.validated_data.get('pwd'))
        if authenticated is None:
            return bad_request('Cannot authenticate user')

        login(request, authenticated)

        serializer = BusinessSerializer(business)
        request.session['business'] = serializer.data

        return Response({
            'business_id': business.pk
        }, status=status.HTTP_200_OK)


class BusinessImageView(LoginRequiredMixin, APIView):
    def post(self, request, business_id):
        file = request.FILES.get('file')
        business = Business.objects.get(pk=business_id)
        business_users = business.users.filter(id=request.user.id)
        if len(business_users) > 0:
            business.image = file
            business.save()

            request.session['business_image'] = business.image.url if business.image and business.image.url else None

            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Cannot upload an image for this business, because of a lack of permissions'
            }, status=status.HTTP_403_FORBIDDEN)


class ResendConfirmationEmailView(LoginRequiredMixin, APIView):
    def get(self, request):
        authenticated_user = request.user
        EmailService().send_confirmation_email(authenticated_user)
        return Response({}, status=status.HTTP_200_OK)
