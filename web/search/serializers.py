from rest_framework import serializers


class StrainESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    strain_slug = serializers.SlugField()
    variety = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255)

    effects = serializers.JSONField()
    benefits = serializers.JSONField()
    side_effects = serializers.JSONField()
    flavor = serializers.JSONField()

    about = serializers.CharField()

    removed_by = serializers.CharField(max_length=20)
    removed_date = serializers.DateTimeField()


class StrainReviewESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rating = serializers.FloatField()
    review = serializers.CharField(allow_blank=True)
    review_approved = serializers.BooleanField()

    created_date = serializers.DateTimeField()
    last_modified_date = serializers.DateTimeField()
