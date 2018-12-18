import factory.faker

from web.system.models import TopPageMetaData


class TopPageMetaDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TopPageMetaData

    path = '/'

    meta_title = factory.Faker('word')
    meta_desc = factory.Faker('word')
    meta_keywords = factory.Faker('word')
    og_type = factory.Faker('word')
    og_title = factory.Faker('word')
    og_description = factory.Faker('word')
    fb_app_id = factory.Faker('word')
    twitter_card = factory.Faker('word')
    twitter_author = factory.Faker('word')
    twitter_site = factory.Faker('word')
    meta_tags = '<meta property="twitter:image:alt" content="test image">'
