from rest_framework import serializers

from web.businesses.models import Business, BusinessLocation


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('id', 'name', 'created_date')


class BusinessLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessLocation
        fields = ('id', 'location_name', 'manager_name', 'location_email', 'primary', 'dispensary', 'delivery',
                  'street1', 'city', 'state', 'zip_code', 'phone', 'ext', 'delivery_radius',
                  'mon_open', 'mon_close', 'tue_open', 'tue_close', 'wed_open', 'wed_close', 'thu_open', 'thu_close',
                  'fri_open', 'fri_close', 'sat_open', 'sat_close', 'sun_open', 'sun_close')

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
