from rest_framework import serializers

from web.businesses.models import Business, BusinessLocation, BusinessLocationMenuItem, phone_number_validator


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('id', 'name', 'created_date')


class MenuItemSerializer(serializers.ModelSerializer):
    business_location_id = serializers.ReadOnlyField(source='business_location.id')
    location = serializers.SerializerMethodField()
    dispensary = serializers.ReadOnlyField(source='business_location.dispensary')
    delivery = serializers.ReadOnlyField(source='business_location.delivery')
    grow_house = serializers.ReadOnlyField(source='business_location.grow_house')
    delivery_radius = serializers.ReadOnlyField(source='business_location.delivery_radius')
    removed_date = serializers.ReadOnlyField(source='business_location.removed_date')

    class Meta:
        model = BusinessLocationMenuItem
        fields = ('price_gram', 'price_eighth', 'price_quarter', 'price_half', 'in_stock',
                  'business_location_id', 'dispensary', 'delivery', 'grow_house',
                  'delivery_radius', 'location', 'removed_date')

    def get_location(self, instance):
        if instance.business_location.lat and instance.business_location.lng:
            return {'lat': instance.business_location.lat, 'lon': instance.business_location.lng}
        return {'lat': 0, 'lon': 0}


class BusinessLocationSerializer(serializers.ModelSerializer):
    grow_details = serializers.DictField()

    class Meta:
        model = BusinessLocation
        fields = ('id', 'location_name', 'manager_name', 'location_email', 'image', 'primary', 'dispensary',
                  'delivery', 'street1', 'city', 'state', 'zip_code', 'phone', 'ext', 'timezone', 'about',
                  'delivery_radius', 'mon_open', 'mon_close', 'tue_open', 'tue_close', 'wed_open', 'wed_close',
                  'thu_open', 'thu_close', 'fri_open', 'fri_close', 'sat_open', 'sat_close', 'sun_open', 'sun_close',
                  'lat', 'lng', 'location_raw', 'slug_name', 'city_slug', 'url', 'urls', 'image_url',
                  'grow_house', 'grow_details', 'formatted_address')
        readonly_fields = ('image_url', 'url', 'urls', 'formatted_address')
        extra_kwargs = {
            'phone': {'validators': [phone_number_validator]},
            'mon_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'mon_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'tue_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'tue_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'wed_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'wed_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'thu_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'thu_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'fri_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'fri_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'sat_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'sat_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'sun_open': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']},
            'sun_close': {'format': '%I:%M %p', 'input_formats': ['%I:%M %p']}
        }
