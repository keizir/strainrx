from rest_framework import serializers

from web.businesses.models import LocationReview, GrowerDispensaryPartnership, \
    BusinessLocationMenuItem, UserFavoriteLocation, BusinessLocationGrownStrainItem
from web.businesses.serializers import BusinessLocationSerializer
from web.search.api.services import StrainDetailsService


class BusinessSignUpSerializer(serializers.Serializer):
    name = serializers.CharField()
    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()
    delivery_radius = serializers.FloatField(required=False)
    grow_house = serializers.BooleanField()
    certified_legal_compliance = serializers.BooleanField()
    is_terms_accepted = serializers.BooleanField()

    email = serializers.CharField()
    pwd = serializers.CharField()
    pwd2 = serializers.CharField()

    street1 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    state = serializers.CharField()
    zip_code = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField()

    lat = serializers.FloatField(allow_null=True)
    lng = serializers.FloatField(allow_null=True)
    location_raw = serializers.JSONField()

    mon_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    mon_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    tue_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    tue_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    wed_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    wed_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    thu_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    thu_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    fri_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    fri_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sat_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sat_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sun_open = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)
    sun_close = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'], allow_null=True, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BusinessLocationMenuItemListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        ret = super().to_representation(data)
        request = self.context['view'].request

        if request.GET.get('ddp') and request.user.is_authenticated():
            strain_ids = [mi.get('strain_id') for mi in ret]

            scores = StrainDetailsService().calculate_srx_scores(strain_ids, request.user)
            if len(scores) > 0:
                for mi in ret:
                    mi['match_score'] = scores.get(mi.get('strain_id'))
        return ret


class BusinessLocationMenuItemSerializer(serializers.ModelSerializer):
    strain_id = serializers.IntegerField(required=False)
    url = serializers.ReadOnlyField(source='strain.get_absolute_url')
    strain_name = serializers.ReadOnlyField(source='strain.name')
    strain_variety = serializers.ReadOnlyField(source='strain.variety')
    report_count = serializers.ReadOnlyField(required=False)

    class Meta:
        model = BusinessLocationMenuItem
        list_serializer_class = BusinessLocationMenuItemListSerializer
        fields = ('id', 'strain_id', 'strain_name', 'strain_variety', 'price_gram',
                  'price_eighth', 'price_quarter', 'price_half', 'in_stock', 'url', 'report_count')

    def __init__(self, instance=None, **kwargs):
        if instance and kwargs.get('data') and kwargs['data'].get('menu_item'):
            kwargs['data'] = kwargs['data']['menu_item']
        super().__init__(instance, **kwargs)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.instance and not attrs.get('strain_id'):
            raise serializers.ValidationError({'strain_id': 'This field is required.'})
        return attrs


class BusinessLocationGrownStrainItemSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField(source='strain.get_absolute_url')
    strain_name = serializers.ReadOnlyField(source='strain.name')
    strain_variety = serializers.ReadOnlyField(source='strain.variety')

    class Meta:
        model = BusinessLocationGrownStrainItem
        fields = ('id', 'strain', 'strain_name', 'strain_variety', 'url')

    def create(self, validated_data):
        validated_data['business_location'] = self.context['view'].location
        return BusinessLocationGrownStrainItem.objects.get_or_create(**validated_data)[0]


class LocationReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationReview
        fields = ('rating', 'review')


class GrowerDispensaryPartnershipSerializer(serializers.ModelSerializer):
    dispensary = BusinessLocationSerializer(required=False)
    dispensary_id = serializers.IntegerField(allow_null=False)
    grower = BusinessLocationSerializer(required=False)
    grower_id = serializers.IntegerField(allow_null=False)

    class Meta:
        model = GrowerDispensaryPartnership
        fields = ('id', 'dispensary', 'dispensary_id', 'grower', 'grower_id')


class UserFavoriteLocationSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='location.location_name')
    image = serializers.SerializerMethodField()
    street1 = serializers.ReadOnlyField(source='location.street1')
    city = serializers.ReadOnlyField(source='location.city')
    state = serializers.ReadOnlyField(source='location.state')
    zip_code = serializers.ReadOnlyField(source='location.zip_code')
    phone = serializers.ReadOnlyField(source='location.phone')
    email = serializers.ReadOnlyField(source='location.location_email')
    url = serializers.ReadOnlyField(source='location.get_absolute_url')

    class Meta:
        model = UserFavoriteLocation
        fields = ('id', 'name', 'image', 'street1', 'city', 'state', 'zip_code',
                  'phone', 'email', 'created_date', 'url')

    def get_image(self, instance):
        if instance.location.image:
            return instance.location.image.url
