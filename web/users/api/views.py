import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from web.users.api.serializers import UserDetailSerializer

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
