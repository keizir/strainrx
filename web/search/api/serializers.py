from rest_framework import serializers

from web.search.models import Strain


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
