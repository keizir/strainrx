from rest_framework import serializers

from web.search.models import Strain


class StrainESSerializer(serializers.ModelSerializer):
    removed_by_id = serializers.ReadOnlyField(source='removed_by')
    name_suggest = serializers.SerializerMethodField()

    class Meta:
        model = Strain
        fields = ('id', 'name', 'strain_slug', 'variety', 'category',
                  'effects', 'benefits', 'side_effects', 'flavor', 'about',
                  'removed_date', 'removed_by_id', 'you_may_also_like_exclude',
                  'name_suggest', 'terpenes', 'cannabinoids')

    def get_name_suggest(self, instance):
        input_variants = [instance.name]
        name_words = instance.name.split(' ')
        for i, name_word in enumerate(name_words):
            if i < len(name_words) - 1:
                input_variants.append('{0} {1}'.format(name_word, name_words[i + 1]))
            else:
                input_variants.append(name_word)
        return {'input': input_variants, 'weight': 100 - len(input_variants)}


class StrainReviewESSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    rating = serializers.FloatField()
    review = serializers.CharField(allow_blank=True)
    review_approved = serializers.BooleanField()

    created_date = serializers.DateTimeField()
    last_modified_date = serializers.DateTimeField()
