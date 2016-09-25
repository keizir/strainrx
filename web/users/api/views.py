import logging
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
from web.users.models import User

logger = logging.getLogger(__name__)


def bad_request(error_message):
    return Response({
        'error': error_message
    }, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(LoginRequiredMixin, APIView):
    def put(self, request, user_id):
        if request.user.id != int(user_id):
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = UserDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        user.name = serializer.validated_data.get('name')
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

        request.session[str(token)] = {'first_name': first_name, 'last_name': last_name}

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
        print (is_age_verified)
        if is_age_verified is None or not is_age_verified:
            return bad_request('Age verification is required')

        user_data['is_age_verified'] = is_age_verified
        request.session[token] = user_data

        return Response({
            'token': token
        }, status=status.HTTP_200_OK)

    def process_step_3(self, request):
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

        if user is not None:
            return bad_request('That email address is already registered')

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

        if not pwd or not pwd2:
            return bad_request('Password is required')

        if len(pwd) < 6:
            return bad_request('Password should be at least 6 characters')

        if not set('[~!@#$%^&*()_-+={}":;\',.<>\|/?]+$').intersection(pwd):
            return bad_request('Password should contain at least 1 special character')

        if pwd != pwd2:
            return bad_request('Passwords don\'t match')

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
        user.email = user_data.get('email')
        user.username = user_data.get('email')
        user.set_password(user_data.get('pwd'))
        user.is_age_verified = user_data.get('is_age_verified')
        user.is_email_verified = False
        user.type = 'consumer'
        user.save()

        EmailService().send_confirmation_email(user)

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
