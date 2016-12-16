import logging
import uuid

from rest_framework import serializers

from web.users.models import User, UserLocation

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'email', 'birth_month', 'birth_day', 'birth_year', 'gender')


class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'is_age_verified', 'email', 'pwd', 'pwd2', 'is_terms_accepted')

    pwd = serializers.CharField()
    pwd2 = serializers.CharField()
    is_terms_accepted = serializers.BooleanField()

    def create(self, validated_data):
        user = User(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            email=validated_data.get('email').lower(),
            username=str(uuid.uuid4())[:30],
            is_age_verified=validated_data.get('is_age_verified'),
            is_email_verified=False,
            proximity=10,
            type='consumer'
        )
        user.set_password(validated_data.get('pwd'))
        user.save()
        return user

    def update(self, instance, validated_data):
        pass


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('street1', 'city', 'state', 'zipcode', 'lat', 'lng', 'location_raw')
