import uuid

from django.core.exceptions import ValidationError

from web.businesses.models import BusinessLocation, Business
from web.users import validators
from web.users.models import User


class BusinessSignUpService:
    def enroll_new_business(self, data):
        user = self.validate_and_create_user(data)
        business = self.validate_and_create_business(data, user)
        self.create_business_locations(data, business)
        return business

    def validate_and_create_user(self, data):
        does_exist = User.objects.filter(email=data.get('email')).exists()
        if does_exist:
            raise ValidationError('There is already an account associated with that email address')

        validators.validate_pwd(data.get('pwd'), data.get('pwd2'))

        if not data.get('is_terms_accepted'):
            raise ValidationError('Agreement is required')

        if not data.get('certified_legal_compliance'):
            raise ValidationError('Certification is required')

        user = User(
            email=data.get('email'),
            username=str(uuid.uuid4())[:30],
            city=data.get('city'),
            state=data.get('state'),
            zipcode=data.get('zip_code'),
            is_age_verified=True,
            is_email_verified=False,
            type='business'
        )
        user.set_password(data.get('pwd'))
        user.save()
        return user

    def validate_and_create_business(self, data, user):
        if not data.get('delivery') and not data.get('dispensary'):
            raise ValidationError('Business type is required')

        if not data.get('certified_legal_compliance'):
            raise ValidationError('Certification is required')

        business = Business(
            name=data.get('name'),
            certified_legal_compliance=data.get('certified_legal_compliance'),
            created_by=user
        )
        business.save()

        business.users.add(user)
        business.save()

        return business

    def create_business_locations(self, data, business):
        location = self.build_business_location(data, business)
        location.primary = True
        location.dispensary = data.get('dispensary')
        location.delivery = data.get('delivery')
        location.save()

    def build_business_location(self, data, business):
        business_location = BusinessLocation(
            business=business,
            location_name=business.name,
            location_email=business.created_by.email,
            street1=data.get('street1'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            phone=data.get('phone'),
            ext=data.get('ext'),
            mon_open=data.get('mon_open'),
            mon_close=data.get('mon_close'),
            tue_open=data.get('tue_open'),
            tue_close=data.get('tue_close'),
            wed_open=data.get('wed_open'),
            wed_close=data.get('wed_close'),
            thu_open=data.get('thu_open'),
            thu_close=data.get('thu_close'),
            fri_open=data.get('fri_open'),
            fri_close=data.get('fri_close'),
            sat_open=data.get('sat_open'),
            sat_close=data.get('sat_close'),
            sun_open=data.get('sun_open'),
            sun_close=data.get('sun_close')
        )
        return business_location
