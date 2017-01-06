from rest_framework import serializers

from web.businesses.models import phone_number_validator


class BusinessSignUpSerializer(serializers.Serializer):
    name = serializers.CharField()
    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()
    certified_legal_compliance = serializers.BooleanField()
    is_terms_accepted = serializers.BooleanField()

    email = serializers.CharField()
    pwd = serializers.CharField()
    pwd2 = serializers.CharField()

    street1 = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    zip_code = serializers.CharField()
    phone = serializers.CharField()
    ext = serializers.CharField(allow_blank=True, allow_null=True)

    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)
    location_raw = serializers.JSONField()

    mon_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    mon_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BusinessLocationDetailSerializer(serializers.Serializer):
    location_name = serializers.CharField()
    manager_name = serializers.CharField(allow_blank=True, allow_null=True)
    location_email = serializers.CharField()

    phone = serializers.CharField(validators=[phone_number_validator])
    ext = serializers.CharField(allow_blank=True, allow_null=True)
    timezone = serializers.CharField(allow_blank=True, allow_null=True)

    about = serializers.CharField(allow_blank=True)

    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()

    delivery_radius = serializers.FloatField(allow_null=True)

    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)
    location_raw = serializers.JSONField(default={})

    mon_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    mon_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    tue_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    wed_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    thu_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    fri_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sat_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)
    sun_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True)

    def update(self, inst, data):
        inst.location_name = data.get('location_name')
        inst.manager_name = data.get('manager_name')
        inst.location_email = data.get('location_email')
        inst.dispensary = data.get('dispensary')
        inst.delivery = data.get('delivery')
        inst.delivery_radius = data.get('delivery_radius')
        inst.phone = data.get('phone')
        inst.ext = data.get('ext')
        inst.timezone = data.get('timezone')
        inst.about = data.get('about')
        inst.lat = data.get('lat') if data.get('lat') else inst.lat
        inst.lng = data.get('lng') if data.get('lng') else inst.lng
        inst.location_raw = data.get('location_raw') if data.get('location_raw') else inst.location_raw
        inst.mon_open = data.get('mon_open')
        inst.mon_close = data.get('mon_close')
        inst.tue_open = data.get('tue_open')
        inst.tue_close = data.get('tue_close')
        inst.wed_open = data.get('wed_open')
        inst.wed_close = data.get('wed_close')
        inst.thu_open = data.get('thu_open')
        inst.thu_close = data.get('thu_close')
        inst.fri_open = data.get('fri_open')
        inst.fri_close = data.get('fri_close')
        inst.sat_open = data.get('sat_open')
        inst.sat_close = data.get('sat_close')
        inst.sun_open = data.get('sun_open')
        inst.sun_close = data.get('sun_close')
        inst.save()

    def create(self, validated_data):
        pass


class BusinessLocationMenuItemSerializer(serializers.Serializer):
    strain_id = serializers.IntegerField()

    price_gram = serializers.FloatField(allow_null=True)
    price_eighth = serializers.FloatField(allow_null=True)
    price_quarter = serializers.FloatField(allow_null=True)
    price_half = serializers.FloatField(allow_null=True)

    in_stock = serializers.BooleanField(default=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
