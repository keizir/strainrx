import logging
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.users.api.serializers import (UserDetailSerializer)
from web.users.models import User

logger = logging.getLogger(__name__)


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
        # serializer = UserLoginSerializer(data=request.data)
        email = request.data.get('email')
        pwd = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None and user.check_password(pwd):
            authenticate(email=user.email, password=user.password)
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
