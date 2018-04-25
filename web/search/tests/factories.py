import random

import factory.faker

from web.search.models import Strain


class StrainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Strain

    name = factory.Faker('name')
    variety = factory.LazyAttribute(lambda x: random.choice(Strain.VARIETY_CHOICES)[0])
    category = factory.LazyAttribute(lambda x: random.choice(Strain.CATEGORY_CHOICES)[0])
