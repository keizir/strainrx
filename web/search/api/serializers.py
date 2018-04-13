from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def get_search_criteria(self):
        self.is_valid()

        step_1_data = self.validated_data.get('step1', {})
        step_2_data = self.validated_data.get('step2', {})
        step_3_data = self.validated_data.get('step3', {})
        step_4_data = self.validated_data.get('step4', {})

        types = 'skipped' if step_1_data.get('skipped') else step_1_data
        effects = 'skipped' if step_2_data.get('skipped') else step_2_data.get('effects', {})
        benefits = 'skipped' if step_3_data.get('skipped') else step_3_data.get('effects', {})
        side_effects = 'skipped' if step_4_data.get('skipped') else step_4_data.get('effects', {})
        return types, effects, benefits, side_effects


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


class StrainSearchSerializer(serializers.ModelSerializer):

    BEST_MATCH, LOCATION, NAME, PRICE = '', 'location', 'name', 'price'

    SORT_CHOICES = (
        (BEST_MATCH, 'best match'),
        (LOCATION, 'location'),
        (NAME, 'name'),
        (PRICE, 'price'),
    )
    SORT_OPTIONS = [key for key, value in SORT_CHOICES]
    SORT_FIELDS = {
        BEST_MATCH: lambda **kwargs: '_score',
        PRICE: lambda **kwargs: {
            'locations.price_gram': {
                "nested_path": "locations",
                'order': 'asc',
                "mode": "min",
                "nested_filter": {
                    "geo_distance": {
                        "distance": "{}mi".format(kwargs.get('proximity')),
                        "distance_type": "plane",
                        "locations.location": {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')}
                    }
                }
            }
        },
        LOCATION: lambda **kwargs: {
            '_geo_distance': {
                'locations.location': {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')},
                "nested_path": "locations",
                'order': 'asc',
                'unit': 'mi',
                'distance_type': 'plane',
                "mode": "min",
                "nested_filter": {
                    "geo_distance": {
                        "distance": "{}mi".format(kwargs.get('proximity')),
                        "distance_type": "plane",
                        "locations.location": {"lat": kwargs.get('lat'), "lon": kwargs.get('lon')}
                    }
                }
            }
        },
        NAME: lambda **kwargs: 'name.raw'
    }

    CANNABINOIDS = ['thc', 'thca', 'thcv', 'cbd', 'cbg', 'cbn', 'cbc']
    TERPENES = ['humulene', 'pinene', 'linalool', 'caryophyllene', 'myrcene', 'terpinolene', 'ocimene', 'limonene',
                'camphene', 'terpineol', 'phellandrene', 'carene', 'pulegone', 'sabinene', 'geraniol', 'valencene']

    q = serializers.CharField(required=False)
    page = serializers.IntegerField(required=False, default=1)
    size = serializers.IntegerField(required=False, default=24, max_value=24)
    start_from = serializers.IntegerField(required=False)
    sort = serializers.MultipleChoiceField(required=False, choices=SORT_CHOICES)

    variety = serializers.MultipleChoiceField(required=False, choices=Strain.VARIETY_CHOICES)
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
    valencene = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Strain
        fields = ('variety', 'cup_winner', 'is_indoor', 'is_clean', 'thc_from', 'thc_to', 'thca_from', 'thca_to',
                  'thcv_from', 'thcv_to', 'cbd_from', 'cbd_to', 'cbg_from', 'cbg_to', 'cbn_from', 'cbn_to', 'cbc_from',
                  'cbc_to', 'humulene', 'pinene', 'linalool', 'caryophyllene', 'myrcene', 'terpinolene', 'ocimene',
                  'limonene', 'camphene', 'terpineol', 'phellandrene', 'carene', 'pulegone', 'sabinene', 'geraniol',
                  'valencene', 'q', 'page', 'size', 'start_from', 'sort')

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except ValidationError as e:
            errors = e.detail
            data = data.copy()
            if errors.pop('page', None):
                data.pop('page')
            if errors.pop('size', None):
                data.pop('size')
            if errors.pop('sort', None):
                sort = data.pop('sort', [])
                data.setlist('sort', [item for item in sort if item in self.SORT_OPTIONS])
            if errors:
                raise ValidationError(errors)
            return super().to_internal_value(data)

    def validate(self, attrs):
        page = attrs.get('page') or self.fields['page'].default
        size = attrs.get('size') or self.fields['size'].default
        attrs['start_from'] = (int(page) - 1) * int(size)
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {key: value for key, value in ret.items() if value}
