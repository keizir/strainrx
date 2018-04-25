# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

from boto.s3.connection import S3Connection, Bucket, Key
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models.query import Q
from django.utils.crypto import get_random_string

from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.businesses.api.permissions import BusinessAccountOwner, BusinessLocationAccountOwnerOrStaff, AllowAnyGetOperation
from web.businesses.api.serializers import *
from web.businesses.api.services import BusinessSignUpService, BusinessLocationService, get_open_closed, \
    get_location_rating, FeaturedBusinessLocationService
from web.businesses.emails import EmailService
from web.businesses.models import Business, BusinessLocation, BusinessLocationMenuItem, LocationReview, \
    UserFavoriteLocation, State, City, BusinessLocationMenuUpdateRequest
from web.businesses.serializers import BusinessSerializer, BusinessLocationSerializer
from web.businesses.utils import NamePaginator
from web.search.api.services import StrainDetailsService
from web.search.models import Strain
from web.users.api.serializers import UserSerializer


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

        if not business.created_by.is_email_verified:
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
            'business_id': business.pk,
            'user': UserSerializer(business.created_by).data
        }, status=status.HTTP_200_OK)


class BusinessImageView(LoginRequiredMixin, APIView):
    permission_classes = (BusinessAccountOwner,)

    def post(self, request, business_id):
        business = Business.objects.get(pk=business_id)

        if business.image and business.image.url:
            conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
            k = Key(bucket=bucket, name=business.image.url.split(bucket.name)[1])
            k.delete()

        file = request.FILES.get('file')
        business.image = file
        business.save()

        request.session['business_image'] = business.image.url if business.image and business.image.url else None

        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationImageView(LoginRequiredMixin, APIView):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)

    def post(self, request, business_id, business_location_id):
        location = BusinessLocation.objects.get(pk=business_location_id)

        if location.image and location.image.url:
            conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
            k = Key(bucket=bucket, name=location.image.url.split(bucket.name)[1])
            k.delete()

        file = request.FILES.get('file')
        location.image = file
        location.save()

        if location.primary:
            request.session['business_image'] = location.image.url

        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationReviewView(APIView):
    permission_classes = (AllowAnyGetOperation,)

    def get(self, request, business_id, business_location_id):
        reviews_raw = LocationReview.objects.filter(location__id=business_location_id,
                                                    review_approved=True).order_by('-created_date')
        reviews = []
        for r in reviews_raw:
            reviews.append(StrainDetailsService.build_review(r))
        return Response({'reviews': reviews}, status=status.HTTP_200_OK)

    def post(self, request, business_id, business_location_id):
        location = BusinessLocation.objects.get(pk=business_location_id)
        serializer = LocationReviewFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review_text = serializer.validated_data.get('review')
        is_approved = False if review_text and len(review_text) > 0 else True
        review = LocationReview(location=location, created_by=request.user,
                                rating=serializer.validated_data.get('rating'),
                                review=review_text, review_approved=is_approved)
        review.save()
        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationFavoriteView(LoginRequiredMixin, APIView):
    def post(self, request, business_id, business_location_id):
        add_to_favorites = request.data.get('like')
        favorite_location = UserFavoriteLocation.objects.filter(location__id=business_location_id,
                                                                created_by=request.user)

        if add_to_favorites and len(favorite_location) == 0:
            favorite_location = UserFavoriteLocation(
                location=BusinessLocation.objects.get(id=business_location_id),
                created_by=request.user
            )
            favorite_location.save()
        elif len(favorite_location) > 0:
            favorite_location[0].delete()

        return Response({}, status=status.HTTP_200_OK)


class ResendConfirmationEmailView(LoginRequiredMixin, APIView):
    def get(self, request):
        authenticated_user = request.user
        EmailService().send_confirmation_email(authenticated_user)
        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationView(APIView):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)

    def get(self, request, business_id, business_location_id):
        if business_location_id == '0':
            locations_raw = BusinessLocation.objects.filter(business__id=business_id, removed_date=None).order_by('id')
            locations = []

            for l in locations_raw:
                serializer = BusinessLocationSerializer(l)
                locations.append(serializer.data)

            return Response({'locations': locations}, status=status.HTTP_200_OK)

        location = BusinessLocation.objects.get(pk=business_location_id)
        serializer = BusinessLocationSerializer(location)
        d = {'location': serializer.data}

        if request.GET.get('ddp'):
            current_user = request.user

            if current_user.is_authenticated():
                d['location']['is_favorite'] = UserFavoriteLocation.objects.filter(location=location,
                                                                                   created_by=current_user).exists()
                d['location']['is_rated'] = LocationReview.objects.filter(location=location,
                                                                          created_by=current_user).exists()

            open_closed = get_open_closed(serializer.data, '%I:%M %p')
            d['location']['rating'] = get_location_rating(business_location_id)
            d['location']['is_open'] = open_closed == 'Opened'
            d['location']['open_closed'] = open_closed

        return Response(d, status=status.HTTP_200_OK)

    def post(self, request, business_id, business_location_id):
        existing_location = BusinessLocation.objects.get(pk=business_location_id)
        serializer = BusinessLocationDetailSerializer(existing_location, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(existing_location, serializer.validated_data)
        return Response({}, status=status.HTTP_200_OK)

    def put(self, request, business_id, business_location_id):
        serializer = BusinessLocationSerializer(data=request.data.get('location'))
        serializer.is_valid(raise_exception=True)

        if int(business_location_id) > 0:
            location = BusinessLocationService().update_location(business_location_id, serializer.validated_data)
        else:
            location = BusinessLocationService().create_location(business_id, serializer.validated_data)

        return Response({
            'location': BusinessLocationSerializer(location).data,
            'image_key': request.data.get('image_key')
        }, status=status.HTTP_200_OK)

    def delete(self, request, business_id, business_location_id):
        BusinessLocationService().remove_location(business_location_id, request.user.id)
        return Response({}, status=status.HTTP_200_OK)


class BusinessLocationMenuView(APIView):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)

    def get(self, request, business_id, business_location_id):
        menu_items_raw = BusinessLocationMenuItem.objects \
            .filter(business_location__id=business_location_id, removed_date=None) \
            .order_by('strain__name')

        menu_items = []
        for mi in menu_items_raw:
            menu_items.append(self.build_menu_item(mi))

        if request.GET.get('ddp') and request.user.is_authenticated():
            strain_ids = []
            for mi in menu_items:
                strain_ids.append(mi.get('strain_id'))

            scores = StrainDetailsService().calculate_srx_scores(strain_ids, request.user)
            if len(scores) > 0:
                for mi in menu_items:
                    mi['match_score'] = scores.get(mi.get('strain_id'))

        return Response({'menu': menu_items}, status=status.HTTP_200_OK)

    def post(self, request, business_id, business_location_id):
        serializer = BusinessLocationMenuItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        strain = Strain.objects.get(pk=data.get('strain_id'))
        location = BusinessLocation.objects.get(pk=business_location_id)

        try:
            menu_item = BusinessLocationMenuItem.objects.get(business_location=location, strain=strain)
            menu_item.in_stock = data.get('in_stock')
            menu_item.price_gram = data.get('price_gram')
            menu_item.price_eighth = data.get('price_eighth')
            menu_item.price_quarter = data.get('price_quarter')
            menu_item.price_half = data.get('price_half')
            menu_item.removed_date = None
        except BusinessLocationMenuItem.DoesNotExist:
            menu_item = BusinessLocationMenuItem(business_location=location, strain=strain,
                                                 price_gram=data.get('price_gram'),
                                                 price_eighth=data.get('price_eighth'),
                                                 price_quarter=data.get('price_quarter'),
                                                 price_half=data.get('price_half'))

        menu_item.save()

        return Response(self.build_menu_item(menu_item), status=status.HTTP_200_OK)

    def put(self, request, business_id, business_location_id):
        menu_item = request.data.get('menu_item')
        item = BusinessLocationMenuItem.objects.get(pk=menu_item.get('id'))
        item.in_stock = menu_item.get('in_stock')
        item.save()
        return Response({}, status=status.HTTP_200_OK)

    def delete(self, request, business_id, business_location_id):
        menu_item_id = request.data.get('menu_item_id')
        item = BusinessLocationMenuItem.objects.get(pk=menu_item_id)
        item.removed_date = datetime.now()
        item.save()
        return Response({}, status=status.HTTP_200_OK)

    def build_menu_item(self, menu_item):
        return {
            'id': menu_item.id,
            'strain_id': menu_item.strain.id,
            'strain_name': menu_item.strain.name,
            'strain_variety': menu_item.strain.variety,
            'price_gram': menu_item.price_gram,
            'price_eighth': menu_item.price_eighth,
            'price_quarter': menu_item.price_quarter,
            'price_half': menu_item.price_half,
            'in_stock': menu_item.in_stock,
            'url': menu_item.strain.get_absolute_url(),
        }


class BusinessLocationMenuUpdateRequestDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, business_id, business_location_id):
        try:
            business_location = BusinessLocation.objects.get(id=business_location_id,
                                                             business_id=business_id)
        except BusinessLocation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        can_request, reason = business_location.can_user_request_menu_update(request.user)

        if not can_request:
            return Response({'error': reason}, status=status.HTTP_400_BAD_REQUEST)

        update_request = BusinessLocationMenuUpdateRequest.objects.create(
            business_location=business_location,
            user=request.user,
            send_notification=request.data.get('send_notification', False),
            message=request.data.get('message', '').strip() or None,
            secret_key=get_random_string(length=64),
        )

        EmailService().send_menu_update_request_email(update_request)

        return Response(status=status.HTTP_201_CREATED)


class BusinessLocationsPerCityView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, state_abbreviation, city_slug):
        if State.objects.filter(abbreviation__iexact=state_abbreviation.lower()).exists():
            state = State.objects.get(abbreviation__iexact=state_abbreviation.lower())
        else:
            return Response({
                "error": "State {0} not found.".format(state_abbreviation)
            }, status=status.HTTP_404_NOT_FOUND)

        if City.objects.filter(state=state, full_name_slug=city_slug).exists():
            city = City.objects.get(state=state, full_name_slug=city_slug)
        else:
            return Response({
                "error": "City {0} not found in the state {1}.".format(city_slug, state_abbreviation)
            }, status=status.HTTP_404_NOT_FOUND)

        filter_kwargs = {}
        grow_house = request.GET.get('grow_house')
        if grow_house == 'true':
            filter_kwargs['grow_house'] = True
        elif grow_house == 'false':
            filter_kwargs['grow_house'] = False

        dispensary = request.GET.get('dispensary')
        if dispensary == 'true':
            filter_kwargs['dispensary'] = True
        elif dispensary == 'false':
            filter_kwargs['dispensary'] = False

        locations = BusinessLocation.objects.filter(city_fk=city, removed_date=None, **filter_kwargs)
        locations = locations.order_by('location_name')
        locations_paged = NamePaginator(locations, on='location_name', per_page=10000)
        data = {}

        for page in locations_paged.pages:
            current_page = []

            for d in page.object_list:
                current_page.append(BusinessLocationSerializer(d).data)

            data[page.start_letter] = current_page

        return Response(data, status=status.HTTP_200_OK)


class FeaturedBusinessLocationsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        try:
            loc_json = json.loads(request.GET.get('loc'))
            location = {
                'latitude': float(loc_json.get('lat')),
                'longitude': float(loc_json.get('lon')),
                'zip_code': loc_json.get('zip'),
            }
        except (TypeError, json.decoder.JSONDecodeError):
            if request.user.is_authenticated():
                try:
                    location = {
                        'latitude': request.user.geo_location.lat,
                        'longitude': request.user.geo_location.lng,
                        'zip_code': request.user.geo_location.zipcode,
                    }
                except ObjectDoesNotExist:
                    location = {}
            else:
                location = {}
        except ValueError:
            return Response({'error': 'Invalid location value'}, status=status.HTTP_400_BAD_REQUEST)

        featured_locations = FeaturedBusinessLocationService().get_list(**location)

        return Response(
            {'locations': [BusinessLocationSerializer(x).data for x in featured_locations]},
            status=status.HTTP_200_OK
        )


class GrowerDispensaryPartnershipListView(APIView):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)

    def get(self, request, business_id, business_location_id):
        grower_filter = request.GET.get('grower_id')
        dispensary_filter = request.GET.get('dispensary_id')

        partnerships = GrowerDispensaryPartnership.objects.select_related('dispensary', 'grower',
                                                                          'dispensary__state_fk',
                                                                          'grower__state_fk',
                                                                          'dispensary__city_fk',
                                                                          'grower__city_fk',
                                                                          )

        if not grower_filter or not dispensary_filter:
            f = Q(grower_id=business_location_id) | Q(dispensary_id=business_location_id)
        elif grower_filter and dispensary_filter:
            f = Q(grower_id=grower_filter) & Q(dispensary_id=dispensary_filter)
        elif grower_filter:
            f = Q(grower_id=grower_filter)
        else:
            f = Q(dispensary_id=dispensary_filter)

        partnerships = partnerships.filter(f)

        return Response(
            {'partnerships': [GrowerDispensaryPartnershipSerializer(x).data for x in partnerships]},
            status=status.HTTP_200_OK
        )

    def post(self, request, business_id, business_location_id):
        data = dict(grower_id=business_location_id, **request.data)
        serializer = GrowerDispensaryPartnershipSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        existing_kwargs = dict(
            grower_id=validated_data['grower_id'],
            dispensary_id=validated_data['dispensary_id'],
        )

        if not GrowerDispensaryPartnership.objects.filter(**existing_kwargs).exists():
            serializer.create(validated_data)

        return Response({}, status=status.HTTP_200_OK)


class GrowerDispensaryPartnershipDetailView(APIView):
    permission_classes = (BusinessLocationAccountOwnerOrStaff,)

    def delete(self, request, business_id, business_location_id, partnership_id):
        GrowerDispensaryPartnership.objects.filter(id=partnership_id).delete()
        return Response({}, status=status.HTTP_200_OK)
