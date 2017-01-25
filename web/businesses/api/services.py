import uuid
from datetime import datetime

import pytz
from django.core.exceptions import ValidationError
from django.db.models import Avg

from web.businesses.models import BusinessLocation, Business, LocationReview
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
    def create_location(self, business_id, location):
        business = Business.objects.get(pk=business_id)
        is_primary_exist = BusinessLocation.objects.filter(business__id=business_id, primary=True,
                                                           removed_date=None).exists()
        l = BusinessLocation(
            business=business,
            primary=not is_primary_exist,
            location_name=location.get('location_name'),
            location_email=location.get('location_email'),
            street1=location.get('street1'),
            city=location.get('city'),
            state=location.get('state'),
            zip_code=location.get('zip_code'),
            phone=location.get('phone'),
            delivery=location.get('delivery'),
            dispensary=location.get('dispensary'),
            delivery_radius=location.get('delivery_radius'),
            lat=location.get('lat'),
            lng=location.get('lng'),
            location_raw=location.get('location_raw') if location.get('location_raw') else {},
            timezone=location.get('timezone'),
            about=location.get('about')
        )
        l.save()
        return l

    def update_location(self, business_location_id, location):
        l = BusinessLocation.objects.get(pk=business_location_id)
        l.location_name = location.get('location_name')
        l.location_email = location.get('location_email')
        l.street1 = location.get('street1')
        l.city = location.get('city')
        l.state = location.get('state')
        l.zip_code = location.get('zip_code')
        l.phone = location.get('phone')
        l.delivery = location.get('delivery')
        l.dispensary = location.get('dispensary')
        l.delivery_radius = location.get('delivery_radius')
        l.lat = location.get('lat') if location.get('lat') else l.lat
        l.lng = location.get('lng') if location.get('lng') else l.lng
        l.location_raw = location.get('location_raw') if location.get('location_raw') else l.location_raw
        l.timezone = location.get('timezone')
        l.about = location.get('about')
        l.save()
        return l

    def remove_location(self, business_location_id, current_user_id):
        l = BusinessLocation.objects.get(pk=business_location_id)
        l.removed_by = current_user_id
        l.removed_date = datetime.now()
        l.save()

        if l.primary:
            locations = BusinessLocation.objects.filter(business__id=l.business.id, removed_date=None).order_by('id')
            if len(locations) > 0:
                new_primary = locations[0]
                new_primary.primary = True
                new_primary.save()


def get_location_rating(location_id):
    rating = LocationReview.objects.filter(location__id=location_id).aggregate(avg_rating=Avg('rating'))
    rating = rating.get('avg_rating')
    return 'Not Rated' if rating is None else "{0:.2f}".format(round(rating, 2))


def get_open_closed(location_json, time_format='%H:%M:%S'):
    days = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    location_tz = pytz.timezone(location_json.get('timezone')) if location_json.get('timezone') else None

    now = datetime.now(tz=location_tz) if location_tz else datetime.now()
    current_day_index = int(now.strftime('%w'))  # 0 - Sunday, 6 - Saturday
    current_hour = int(now.strftime('%H'))
    current_minute = int(now.strftime('%M'))

    loc_o = location_json.get('{0}_open'.format(days[current_day_index]))
    loc_c = location_json.get('{0}_close'.format(days[current_day_index]))

    if loc_o and loc_c:
        loc_o = datetime.strptime(loc_o, time_format)
        loc_c = datetime.strptime(loc_c, time_format)
        now = datetime.strptime('1900-01-01 {0}:{1}'.format(current_hour, current_minute), '%Y-%m-%d %H:%M')

        if location_tz:
            loc_o = location_tz.localize(loc_o)
            loc_c = location_tz.localize(loc_c)
            now = location_tz.localize(now)

        delta = (loc_c - now).total_seconds()
        till_close_min = delta / 60

        if 0 < till_close_min <= 30:
            return 'Closing Soon'

        return 'Opened' if int(loc_o.strftime('%H')) < current_hour < int(loc_c.strftime('%H')) else 'Closed Now'

    return ''
