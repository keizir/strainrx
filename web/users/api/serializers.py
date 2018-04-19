import logging
import uuid

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError

from web.system.models import SystemProperty
from web.users import validators
from web.users.models import User, UserLocation

logger = logging.getLogger(__name__)


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('street1', 'city', 'state', 'zipcode', 'lat', 'lng', 'location_raw')


class UserSerializer(serializers.ModelSerializer):
    geo_location = UserLocationSerializer(read_only=True, allow_null=True)

    class Meta:
        model = User
        exclude = ('password',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'email', 'birth_month', 'birth_day', 'birth_year', 'gender',
                  'timezone')


class UserSignUpSerializer(serializers.ModelSerializer):
    pwd = serializers.CharField()
    pwd2 = serializers.CharField()
    is_terms_accepted = serializers.BooleanField()

    class Meta:
        model = User
        fields = ('name', 'first_name', 'last_name', 'is_age_verified', 'email', 'pwd', 'pwd2', 'is_terms_accepted')
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        if not attrs.get('is_terms_accepted'):
            raise ValidationError({'is_terms_accepted': ['This field is required.']})
        if not attrs.get('is_age_verified'):
            raise ValidationError({'is_age_verified': ['This field is required.']})

        attrs['email'] = attrs['email'].lower()
        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise ValidationError({'email': ['There is already an account associated with that email address']})

        try:
            validators.validate_pwd(attrs.get('pwd'), attrs.get('pwd2'))
        except DjangoValidationError as e:
            raise ValidationError({'pwd': e.messages, 'pwd2': e.messages})

        try:
            validators.validate_name(attrs.get('name'), None)
        except DjangoValidationError as e:
            raise ValidationError({'name': e.messages})
        return attrs

    def save(self, **kwargs):
        proximity = SystemProperty.objects.max_delivery_radius()

        user = User(
            name=self.validated_data.get('name'),
            first_name=self.validated_data.get('first_name'),
            last_name=self.validated_data.get('last_name'),
            email=self.validated_data.get('email').lower(),
            username=str(uuid.uuid4())[:30],
            is_age_verified=self.validated_data.get('is_age_verified'),
            is_email_verified=False,
            proximity=proximity,
            type='consumer'
        )
        user.set_password(self.validated_data.get('pwd'))
        user.save()
        return user
