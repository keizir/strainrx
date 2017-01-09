import datetime
import logging
import uuid

from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.businesses.models import Business, BusinessLocation
from web.businesses.serializers import BusinessSerializer
from web.search.api.serializers import SearchCriteriaSerializer
from web.search.models import UserSearch, StrainReview, StrainImage, UserFavoriteStrain
from web.search.services import build_strain_rating
from web.users import validators
from web.users.api.permissions import UserAccountOwner
from web.users.api.serializers import (UserDetailSerializer, UserSignUpSerializer, UserLocationSerializer)
from web.users.emails import EmailService
from web.users.models import User, PwResetLink, UserSetting, UserLocation

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class UsersView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        email = request.GET.get('email')
        does_exist = User.objects.filter(email=email).exists()
        return Response({'exist': does_exist}, status=status.HTTP_200_OK)


class UserDetailView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def put(self, request, user_id):
        request_data = request.data
        location_data = request.data.get('location')

        del request_data['location']

        serializer = UserDetailSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=user_id)

        if user.email != serializer.validated_data.get('email'):
            try:
                validators.validate_email(serializer.validated_data.get('email'))
            except ValidationError as e:
                return bad_request(e.message)

            does_exist = User.objects.filter(email=serializer.validated_data.get('email')).exists()
            if does_exist:
                raise ValidationError('There is already an account associated with that email address')

        user.name = serializer.validated_data.get('name')
        user.first_name = serializer.validated_data.get('first_name')
        user.last_name = serializer.validated_data.get('last_name')
        user.email = serializer.validated_data.get('email').lower()
        user.birth_month = serializer.validated_data.get('birth_month')
        user.birth_day = serializer.validated_data.get('birth_day')
        user.birth_year = serializer.validated_data.get('birth_year')
        user.gender = serializer.validated_data.get('gender')
        user.timezone = serializer.validated_data.get('timezone')
        user.save()

        serializer = UserLocationSerializer(data=location_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            location = UserLocation.objects.get(user__id=user_id)
            location.street1 = data.get('street1')
            location.city = data.get('city')
            location.state = data.get('state')
            location.zipcode = data.get('zipcode')
            location.lat = data.get('lat')
            location.lng = data.get('lng')
            location.location_raw = data.get('location_raw')
        except UserLocation.DoesNotExist:
            location = UserLocation(
                user=request.user,
                street1=data.get('street1'), city=data.get('city'),
                state=data.get('state'), zipcode=data.get('zipcode'),
                lat=data.get('lat'), lng=data.get('lng'), location_raw=data.get('location_raw')
            )

        location.save()
        return Response({}, status=status.HTTP_200_OK)


class UserChangePwdView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def post(self, request, user_id):
        user = User.objects.get(pk=user_id)
        current_pwd = request.data.get('curPwd')

        does_match = user.check_password(current_pwd)
        if not does_match:
            return bad_request('Current password you entered does not match our entry')

        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')
        if pwd and pwd2:
            try:
                validators.validate_pwd(pwd, pwd2)
                user.set_password(pwd)
                user.save()
            except ValidationError as e:
                return bad_request(e.message)

        return Response({}, status=status.HTTP_200_OK)


class UserSettingsView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        settings_raw = UserSetting.objects.filter(user=user)
        settings = []

        for s in settings_raw:
            settings.append({
                'setting_name': s.setting_name,
                'setting_value': s.setting_value
            })

        return Response(settings, status=status.HTTP_200_OK)

    def post(self, request, user_id):
        setting_name = request.data.get('setting_name')
        setting_value = request.data.get('setting_value')
        user = User.objects.get(pk=user_id)

        try:
            setting = UserSetting.objects.get(setting_name=setting_name, user=user)
        except UserSetting.DoesNotExist:
            setting = UserSetting(setting_name=setting_name, user=user)

        setting.setting_value = setting_value
        setting.save()

        return Response({}, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        pwd = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return bad_request('Email or password does not match')

        does_match = user.check_password(pwd)
        if not does_match:
            return bad_request('Email or password does not match')

        authenticated = authenticate(username=user.email, password=pwd)
        if authenticated is None:
            return bad_request('Email or password does not match')

        # If user is a business user we need a business object to be available across the app
        if user.type == 'business':
            business = Business.objects.filter(users__in=[user])[:1]
            request.session['business'] = BusinessSerializer(business[0]).data

            locations = BusinessLocation.objects.filter(business__id=business[0].id, primary=True, removed_date=None)
            if len(locations) > 0:
                primary = locations[0]
                business_image = primary.image.url if len(
                    locations) > 0 and primary.image and primary.image.url else None
                request.session['business_image'] = business_image

        login(request, authenticated)
        return Response({}, status=status.HTTP_200_OK)


class UserSignUpWizardView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        request_data = request.data
        location_data = request.data.get('location')
        del request_data['location']

        user_serializer = UserSignUpSerializer(data=request_data)
        location_serializer = UserLocationSerializer(data=location_data)

        try:
            user_serializer.is_valid(raise_exception=True)
            location_serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return bad_request(e.message)

        user_data = user_serializer.validated_data
        l_data = location_serializer.validated_data

        if User.objects.filter(email=user_data.get('email')).exists():
            return bad_request('There is already an account associated with that email address')

        try:
            validators.validate_pwd(user_data.get('pwd'), user_data.get('pwd2'))
        except ValidationError as e:
            return bad_request(e.message)

        if not user_data.get('is_terms_accepted'):
            return bad_request('Agreement is required')

        try:
            user = user_serializer.save()
            location = UserLocation(user=user, street1=l_data.get('street1'), city=l_data.get('city'),
                                    state=l_data.get('state'), zipcode=l_data.get('zipcode'),
                                    lat=l_data.get('lat'), lng=l_data.get('lng'),
                                    location_raw=l_data.get('location_raw'))
            location.save()
        except Exception:
            logger.exception('Cannot sign up user')

            if UserLocation.objects.filter(user__email=user_data.get('email')).exists():
                l = UserLocation.objects.get(user__email=user_data.get('email'))
                l.delete()

            if User.objects.filter(email=user_data.get('email')).exists():
                u = User.objects.get(email=user_data.get('email'))
                u.delete()

            return bad_request('Something gone wrong. Please, try again.')

        authenticated = authenticate(username=user.email, password=user_data.get('pwd'))
        if authenticated is None:
            return bad_request('Cannot authenticate user')

        login(request, authenticated)

        try:
            EmailService().send_confirmation_email(user)
        except Exception:
            logger.exception('Cannot send an email to {0}'.format(user.email))

        return Response({}, status=status.HTTP_200_OK)


class ResendConfirmationEmailView(LoginRequiredMixin, APIView):
    def get(self, request):
        authenticated_user = request.user
        EmailService().send_confirmation_email(authenticated_user)
        return Response({}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        user_id = request.GET.get('uid')
        token = request.GET.get('t')

        if not user_id or not token:
            return bad_request('Cannot validate your token. Please, try to reset you password one more time.')

        try:
            user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            return bad_request('There is no user to reset password for.')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            return bad_request('Cannot validate this reset link. Please, try to reset you password one more time.')

        if link.token != token:
            return bad_request('This link is invalid. Please, try to reset you password one more time.')

        now = datetime.datetime.now()
        delta = now - link.last_modified_date.replace(tzinfo=None)

        if delta.days >= 2:
            return bad_request('This link is inactive. Please, try to reset you password one more time.')

        return Response({}, status=status.HTTP_200_OK)

    def post(self, request):
        action = request.data.get('action')

        if action == 'send-reset-email':
            return self.process_send_reset_email_action(request)

        if action == 'reset-pwd':
            return self.process_reset_pwd_action(request)

        return bad_request('Cannot determine required action.')

    def process_send_reset_email_action(self, request):
        email = request.data.get('email')

        if not email:
            return bad_request('Email is required')

        try:
            validator = EmailValidator()
            validator.__call__(email)
        except ValidationError:
            return bad_request('Invalid email format')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is None:
            return bad_request('There is no account registered for this email')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            link = PwResetLink()

        token = '{0}-{1}'.format(uuid.uuid4(), uuid.uuid4())
        link.user = user
        link.token = token
        link.last_modified_date = datetime.datetime.now()
        link.save()

        EmailService().send_reset_pwd_email(user, token)

        return Response({}, status=status.HTTP_200_OK)

    def process_reset_pwd_action(self, request):
        user_id = request.data.get('uid')
        token = request.data.get('t')
        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')

        if not user_id or not token:
            return bad_request('Cannot validate your token. Please, try to reset you password one more time.')

        try:
            user = User.objects.get(pk=int(user_id))
        except User.DoesNotExist:
            return bad_request('There is no user to reset password for.')

        try:
            link = PwResetLink.objects.get(user=user)
        except PwResetLink.DoesNotExist:
            return bad_request('Cannot validate this reset link. Please, try to reset you password one more time.')

        if link.token != token:
            return bad_request('This link is invalid. Please, try to reset you password one more time.')

        now = datetime.datetime.now()
        delta = now - link.last_modified_date.replace(tzinfo=None)

        if delta.days >= 2:
            return bad_request('This link is inactive. Please, try to reset you password one more time.')
        try:
            validators.validate_pwd(pwd, pwd2)
        except ValidationError as e:
            return bad_request(e.message)

        user.set_password(pwd)
        user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserStrainSearchesView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        try:
            user_search = UserSearch.objects.get(user=request.user)
            return Response({'strain_search': user_search}, status=status.HTTP_200_OK)
        except UserSearch.DoesNotExist:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
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

        try:
            user_search = UserSearch.objects.get(user=request.user)
        except UserSearch.DoesNotExist:
            user_search = UserSearch(user=request.user)

        user_search.varieties = types
        user_search.effects = effects
        user_search.benefits = benefits
        user_search.side_effects = side_effects
        user_search.save()

        return Response({}, status=status.HTTP_200_OK)


class StrainRatingView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        raw = StrainReview.objects.filter(created_by__id=user_id).order_by('-created_date')
        ratings = []
        for r in raw:
            images = StrainImage.objects.filter(strain=r.strain)
            ratings.append({
                'id': r.id,
                'strain_id': r.strain.id,
                'strain_name': r.strain.name,
                'strain_slug': r.strain.strain_slug,
                'strain_variety': r.strain.variety,
                'strain_image': images[0] if len(images) > 0 else None,
                'strain_overall_rating': build_strain_rating(r.strain),
                'rating': r.rating,
                'review': r.review,
                'created_date': r.created_date
            })
        return Response({'reviews': ratings}, status=status.HTTP_200_OK)


class UserFavoritesView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id, favorite_type, favorite_id):
        if 'strain' == favorite_type:
            favorites_raw = UserFavoriteStrain.objects.filter(created_by__id=user_id).order_by('-created_date')
            favorites = []
            for r in favorites_raw:
                images = StrainImage.objects.filter(strain=r.strain, is_approved=True)
                img = images[0].image.url if len(images) > 0 and images[0].image and images[0].image.url else None
                favorites.append({
                    'id': r.id,
                    'strain_id': r.strain.id,
                    'strain_name': r.strain.name,
                    'strain_slug': r.strain.strain_slug,
                    'strain_variety': r.strain.variety,
                    'strain_image': img,
                    'strain_overall_rating': build_strain_rating(r.strain),
                    'created_date': r.created_date
                })
            return Response({'favorites': favorites}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, favorite_type, favorite_id):
        if 'strain' == favorite_type:
            favorite = UserFavoriteStrain.objects.get(pk=favorite_id)
            favorite.delete()
            return Response({}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_400_BAD_REQUEST)


class UserGeoLocationView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def get(self, request, user_id):
        if UserLocation.objects.filter(user__id=user_id).exists():
            location = UserLocation.objects.get(user__id=user_id)
            return Response({'location': UserLocationSerializer(location).data}, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, user_id):
        serializer = UserLocationSerializer(data=request.data.get('address'))
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            location = UserLocation.objects.get(user__id=user_id)
            location.street1 = data.get('street1')
            location.city = data.get('city')
            location.state = data.get('state')
            location.zipcode = data.get('zipcode')
            location.lat = data.get('lat')
            location.lng = data.get('lng')
            location.location_raw = data.get('location_raw') if data.get('location_raw') else {}
        except UserLocation.DoesNotExist:
            location = UserLocation(
                user=request.user,
                street1=data.get('street1'), city=data.get('city'),
                state=data.get('state'), zipcode=data.get('zipcode'),
                lat=data.get('lat'), lng=data.get('lng'),
                location_raw=data.get('location_raw') if data.get('location_raw') else {}
            )

        location.save()

        if request.data.get('timezone'):
            user = User.objects.get(pk=request.user.id)
            user.timezone = request.data.get('timezone')
            user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserProximityView(LoginRequiredMixin, APIView):
    permission_classes = (UserAccountOwner,)

    def post(self, request, user_id):
        user = User.objects.get(pk=user_id)
        user.proximity = request.data.get('proximity')
        user.save()
        return Response({}, status=status.HTTP_200_OK)
