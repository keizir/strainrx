from rest_framework import serializers


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

    phone = serializers.CharField()
    ext = serializers.CharField(allow_blank=True, allow_null=True)

    dispensary = serializers.BooleanField()
    delivery = serializers.BooleanField()

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

    def update(self, instance, validated_data):
        instance.location_name = validated_data.get('location_name')
        instance.manager_name = validated_data.get('manager_name')
        instance.location_email = validated_data.get('location_email')
        instance.dispensary = validated_data.get('dispensary')
        instance.delivery = validated_data.get('delivery')
        instance.phone = validated_data.get('phone')
        instance.ext = validated_data.get('ext')
        instance.mon_open = validated_data.get('mon_open')
        instance.mon_close = validated_data.get('mon_close')
        instance.tue_open = validated_data.get('tue_open')
        instance.tue_close = validated_data.get('tue_close')
        instance.wed_open = validated_data.get('wed_open')
        instance.wed_close = validated_data.get('wed_close')
        instance.thu_open = validated_data.get('thu_open')
        instance.thu_close = validated_data.get('thu_close')
        instance.fri_open = validated_data.get('fri_open')
        instance.fri_close = validated_data.get('fri_close')
        instance.sat_open = validated_data.get('sat_open')
        instance.sat_close = validated_data.get('sat_close')
        instance.sun_open = validated_data.get('sun_open')
        instance.sun_close = validated_data.get('sun_close')
        instance.save()

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
