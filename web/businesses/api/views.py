# -*- coding: utf-8 -*-
import logging

from boto.s3.connection import S3Connection, Bucket, Key
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.businesses.api.serializers import BusinessSignUpSerializer, BusinessLocationDetailSerializer
from web.businesses.api.services import BusinessSignUpService
from web.businesses.emails import EmailService
from web.businesses.models import Business, BusinessLocation
from web.businesses.serializers import BusinessSerializer, BusinessLocationSerializer

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

        if business.image and business.image.url:
            conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
            k = Key(bucket=bucket, name=business.image.url.split(bucket.name)[1])
            k.delete()

        business.image = file
        business.save()

        request.session['business_image'] = business.image.url if business.image and business.image.url else None

        return Response({}, status=status.HTTP_200_OK)


class ResendConfirmationEmailView(LoginRequiredMixin, APIView):
    def get(self, request):
        authenticated_user = request.user
        EmailService().send_confirmation_email(authenticated_user)
        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationView(LoginRequiredMixin, APIView):
    def get(self, request, business_id, business_location_id):
        location = BusinessLocation.objects.get(pk=business_location_id)
        serializer = BusinessLocationSerializer(location)
        return Response({'location': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, business_id, business_location_id):
        serializer = BusinessLocationDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        business_location = BusinessLocation.objects.get(pk=business_location_id)
        business_location.location_name = data.get('location_name')
        business_location.manager_name = data.get('manager_name')
        business_location.location_email = data.get('location_email')
        business_location.dispensary = data.get('dispensary')
        business_location.delivery = data.get('delivery')
        business_location.phone = data.get('phone')
        business_location.ext = data.get('ext')
        business_location.mon_open = data.get('mon_open')
        business_location.mon_close = data.get('mon_close')
        business_location.tue_open = data.get('tue_open')
        business_location.tue_close = data.get('tue_close')
        business_location.wed_open = data.get('wed_open')
        business_location.wed_close = data.get('wed_close')
        business_location.thu_open = data.get('thu_open')
        business_location.thu_close = data.get('thu_close')
        business_location.fri_open = data.get('fri_open')
        business_location.fri_close = data.get('fri_close')
        business_location.sat_open = data.get('sat_open')
        business_location.sat_close = data.get('sat_close')
        business_location.sun_open = data.get('sun_open')
        business_location.sun_close = data.get('sun_close')

        business_location.save()

        return Response({}, status=status.HTTP_200_OK)
