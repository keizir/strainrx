from rest_framework import serializers

from web.search.models import Strain, StrainReview, StrainRating, StrainImage


class SearchCriteriaSerializer(serializers.Serializer):
    step1 = serializers.DictField()
    step2 = serializers.DictField()
    step3 = serializers.DictField()
    step4 = serializers.DictField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class StrainDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = ('name', 'strain_slug', 'variety', 'category',
                  'effects', 'benefits', 'side_effects', 'flavor', 'about')


class StrainRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainRating
        fields = ('effects', 'effects_changed', 'benefits', 'benefits_changed', 'side_effects', 'side_effects_changed',
                  'status')


class StrainReviewFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainReview
        fields = ('rating', 'review')


class StrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrainImage
