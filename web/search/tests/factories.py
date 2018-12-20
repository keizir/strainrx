import random

import factory.faker
from django.db.models.signals import post_save

from web.search.models import Strain


@factory.django.mute_signals(post_save)
class StrainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Strain

    name = factory.Faker('name')
    variety = factory.LazyAttribute(lambda x: random.choice(Strain.VARIETY_CHOICES)[0])
    category = factory.LazyAttribute(lambda x: random.choice(Strain.CATEGORY_CHOICES)[0])
