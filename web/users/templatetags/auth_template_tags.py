from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def http_username():
    return settings.HTTP_USERNAME


@register.simple_tag
def http_password():
    return settings.HTTP_PASSWORD


@register.simple_tag
def google_maps_api_url():
    return 'https://maps.google.com/maps/api/js?key={0}&libraries=places&sensor=false'.format(settings.GOOGLE_API_KEY)


@register.simple_tag
def google_maps_api_key():
    return settings.GOOGLE_API_KEY
