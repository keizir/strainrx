from rest_framework import serializers


class StrainReviewESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rating = serializers.FloatField()
    review = serializers.CharField(allow_blank=True)
    review_approved = serializers.BooleanField()

    created_date = serializers.DateTimeField()
    last_modified_date = serializers.DateTimeField()
