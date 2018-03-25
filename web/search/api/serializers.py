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
                  'effects', 'benefits', 'side_effects', 'flavor', 'about', 'variety_image')


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


class SearchSerializer(serializers.ModelSerializer):
    # cannabinoids
    thc_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    thc_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    thca_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    thca_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    thcv_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    thcv_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbd_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbd_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbg_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbg_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbn_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbn_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbc_from = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)
    cbc_to = serializers.IntegerField(allow_null=True, min_value=0, max_value=100, required=False)

    # terpenes
    humulene = serializers.BooleanField(default=False, required=False)
    pinene = serializers.BooleanField(default=False, required=False)
    linalool = serializers.BooleanField(default=False, required=False)
    caryophyllene = serializers.BooleanField(default=False, required=False)
    myrcene = serializers.BooleanField(default=False, required=False)
    terpinolene = serializers.BooleanField(default=False, required=False)
    ocimene = serializers.BooleanField(default=False, required=False)
    limonene = serializers.BooleanField(default=False, required=False)
    camphene = serializers.BooleanField(default=False, required=False)
    terpineol = serializers.BooleanField(default=False, required=False)
    phellandrene = serializers.BooleanField(default=False, required=False)
    carene = serializers.BooleanField(default=False, required=False)
    pulegone = serializers.BooleanField(default=False, required=False)
    sabinene = serializers.BooleanField(default=False, required=False)
    geraniol = serializers.BooleanField(default=False, required=False)

    style = {'template_pack': 'rest_framework/vertical/'}

    class Meta:
        model = Strain
        fields = ('variety', 'cup_winner', 'is_indoor', 'is_clean', 'thc_from', 'thc_to', 'thca_from', 'thca_to',
                  'thcv_from', 'thcv_to', 'cbd_from', 'cbd_to', 'cbg_from', 'cbg_to', 'cbn_from', 'cbn_to', 'cbc_from',
                  'cbc_to', 'humulene', 'pinene', 'linalool', 'caryophyllene', 'myrcene', 'terpinolene', 'ocimene',
                  'limonene', 'camphene', 'terpineol', 'phellandrene', 'carene', 'pulegone', 'sabinene', 'geraniol')
