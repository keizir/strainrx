import logging
from rest_framework import serializers

from web.users.models import User

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'email',
                  'city', 'state', 'zipcode',
                  'birth_month', 'birth_day', 'birth_year', 'gender')
