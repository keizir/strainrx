import uuid
from datetime import datetime

from django.core.exceptions import ValidationError

from web.businesses.models import BusinessLocation, Business
from web.users import validators
from web.users.models import User, UserLocation


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
            is_age_verified=True,
            is_email_verified=False,
            type='business'
        )
        user.set_password(data.get('pwd'))
        user.save()

        location = UserLocation(user=user, street1=data.get('street1'), city=data.get('city'),
                                state=data.get('state'), zipcode=data.get('zip_code'),
                                lat=data.get('lat'), lng=data.get('lng'), location_raw=data.get('location_raw'))
        location.save()

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
            lat=data.get('lat'),
            lng=data.get('lng'),
            location_raw=data.get('location_raw'),
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


class BusinessLocationService:
    def update_locations(self, business_id, to_update_locations):
        for to_update in to_update_locations:
            data = to_update.get('data')
            if to_update.get('location_id'):
                l = BusinessLocation.objects.get(pk=to_update.get('location_id'))
                l.location_name = data.get('location_name')
                l.street1 = data.get('street1')
                l.city = data.get('city')
                l.state = data.get('state')
                l.zip_code = data.get('zip_code')
                l.delivery = data.get('delivery')
                l.dispensary = data.get('dispensary')
                l.delivery_radius = data.get('delivery_radius')
                l.lat = data.get('lat') if data.get('lat') else l.lat
                l.lng = data.get('lng') if data.get('lng') else l.lng
                l.location_raw = data.get('location_raw') if data.get('location_raw') else l.location_raw
                l.save()
            else:
                business = Business.objects.get(pk=business_id)
                location = BusinessLocation(
                    business=business,
                    location_name=data.get('location_name'),
                    street1=data.get('street1'),
                    city=data.get('city'),
                    state=data.get('state'),
                    zip_code=data.get('zip_code'),
                    delivery=data.get('delivery'),
                    dispensary=data.get('dispensary'),
                    delivery_radius=data.get('delivery_radius'),
                    lat=data.get('lat'),
                    lng=data.get('lng'),
                    location_raw=data.get('location_raw') if data.get('location_raw') else {}
                )
                location.save()

    def remove_location(self, business_location_id, current_user_id):
        location = BusinessLocation.objects.get(pk=business_location_id)
        location.removed_by = current_user_id
        location.removed_date = datetime.now()
        location.save()
