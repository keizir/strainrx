import factory.faker

from web.businesses.models import Business, BusinessLocation
from web.users.tests.factories import BusinessUserFactory


class BusinessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Business

    name = factory.Faker('name')
    created_by = factory.SubFactory(BusinessUserFactory)
    is_active = True
    account_type = 'house_account'

    @factory.post_generation
    def location(self, create, extracted, **kwargs):
        if not create:
            return
        BusinessLocationFactory(business=self)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        self.users.add(self.created_by)
        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.users.add(user)


class BusinessLocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusinessLocation

    business = factory.SubFactory(BusinessFactory)
    location_name = factory.Faker('name')
    street1 = factory.Faker('name')
    city = 'New York'
    state = 'US'
    zip_code = '12365'
    lat = 0
    lng = 0
