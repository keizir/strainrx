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

from web.users.api.serializers import (UserDetailSerializer)
from web.users.emails import EmailService
from web.users.models import User, PwResetLink

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


def validate_pwd(pwd, pwd2):
    if not pwd or not pwd2:
        return bad_request('Password is required')

    if len(pwd) < 6:
        return bad_request('Password should be at least 6 characters')

    if not set('[~!@#$%^&*()_-+={}":;\',.<>\|/?]+$').intersection(pwd):
        return bad_request('Password should contain at least 1 special character')

    if pwd != pwd2:
        return bad_request('Passwords don\'t match')


def validate_email(email):
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

    if user is not None:
        return bad_request('That email address is already registered')


class UserDetailView(LoginRequiredMixin, APIView):
    def put(self, request, user_id):
        if request.user.id != int(user_id):
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = UserDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(pk=user_id)

        if user.email != serializer.validated_data.get('email'):
            valid_email = validate_email(serializer.validated_data.get('email'))
            if isinstance(valid_email, Response):
                return valid_email

        user.name = serializer.validated_data.get('name')
        user.first_name = serializer.validated_data.get('first_name')
        user.last_name = serializer.validated_data.get('last_name')
        user.email = serializer.validated_data.get('email').lower()
        user.city = serializer.validated_data.get('city')
        user.state = serializer.validated_data.get('state')
        user.zipcode = serializer.validated_data.get('zipcode')
        user.birth_month = serializer.validated_data.get('birth_month')
        user.birth_day = serializer.validated_data.get('birth_day')
        user.birth_year = serializer.validated_data.get('birth_year')
        user.gender = serializer.validated_data.get('gender')
        user.save()

        return Response({}, status=status.HTTP_200_OK)


class UserChangePwdView(LoginRequiredMixin, APIView):
    def post(self, request, user_id):
        if request.user.id != int(user_id):
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        user = User.objects.get(pk=user_id)
        current_pwd = request.data.get('curPwd')

        does_match = user.check_password(current_pwd)
        if not does_match:
            return bad_request('Current password you entered does not match our entry')

        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')
        if pwd and pwd2:
            pwd_valid = validate_pwd(pwd, pwd2)
            if isinstance(pwd_valid, Response):
                return pwd_valid
            user.set_password(pwd)

        user.save()

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

        login(request, authenticated)
        return Response({}, status=status.HTTP_200_OK)


class UserSignUpWizardView(APIView):
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

        if step == 5:
            return self.process_step_5(request)

    def process_step_1(self, request):
        token = self.check_enrollment_token(request)
        if isinstance(token, Response):
            return token

        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')

        if not first_name:
            return bad_request('First Name is required')

        if not last_name:
            return bad_request('Last Name is required')

        user_data = self.get_user_data(request, token)
        if isinstance(user_data, Response):
            user_data = {}

        user_data['first_name'] = first_name
        user_data['last_name'] = last_name

        request.session[str(token)] = user_data

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def process_step_2(self, request):
        token = self.check_enrollment_token(request)
        if isinstance(token, Response):
            return token

        user_data = self.get_user_data(request, token)
        if isinstance(user_data, Response):
            return user_data

        is_age_verified = request.data.get('age')
        if is_age_verified is None or not is_age_verified:
            return bad_request('Age verification is required')

        user_data['is_age_verified'] = is_age_verified
        request.session[token] = user_data

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def process_step_3(self, request):
        email = request.data.get('email')
        valid_email = validate_email(email)
        if isinstance(valid_email, Response):
            return valid_email

        token = self.check_enrollment_token(request)
        if isinstance(token, Response):
            return token

        user_data = self.get_user_data(request, token)
        if isinstance(user_data, Response):
            return user_data

        user_data['email'] = email
        request.session[token] = user_data

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def process_step_4(self, request):
        pwd = request.data.get('pwd')
        pwd2 = request.data.get('pwd2')

        pwd_valid = validate_pwd(pwd, pwd2)
        if isinstance(pwd_valid, Response):
            return pwd_valid

        token = self.check_enrollment_token(request)
        if isinstance(token, Response):
            return token

        user_data = self.get_user_data(request, token)
        if isinstance(user_data, Response):
            return user_data

        user_data['pwd'] = pwd
        request.session[token] = user_data

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def process_step_5(self, request):
        agreed = request.data.get('agreed')

        if not agreed:
            return bad_request('Agreement is required')

        token = self.check_enrollment_token(request)
        if isinstance(token, Response):
            return token

        user_data = self.get_user_data(request, token)
        if isinstance(user_data, Response):
            return user_data

        try:
            user = User.objects.get(email=user_data.get('email'))
        except User.DoesNotExist:
            user = None

        if user is not None:
            return bad_request('This email address is already registered')

        user = User()
        user.first_name = user_data.get('first_name')
        user.last_name = user_data.get('last_name')
        user.email = user_data.get('email').lower()
        user.username = str(uuid.uuid4())[:30]
        user.set_password(user_data.get('pwd'))
        user.is_age_verified = user_data.get('is_age_verified')
        user.is_email_verified = False
        user.type = 'consumer'
        user.save()

        try:
            EmailService().send_confirmation_email(user)
        except Exception as e:
            print('Cannot send an email to ' + user.email)

        authenticated = authenticate(username=user.email, password=user_data.get('pwd'))
        if authenticated is None:
            return bad_request('Cannot authenticate user')

        login(request, authenticated)

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def check_enrollment_token(self, request):
        t_val = request.session['t_val']
        token = request.data.get('token')

        if t_val != token:
            return bad_request('Invalid session')

        return token

    def get_user_data(self, request, token):
        user_data = request.session.get(token)

        if user_data is None:
            return bad_request('Invalid session')

        return user_data


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

        pwd_valid = validate_pwd(pwd, pwd2)
        if isinstance(pwd_valid, Response):
            return pwd_valid

        user.set_password(pwd)
        user.save()

        return Response({}, status=status.HTTP_200_OK)
