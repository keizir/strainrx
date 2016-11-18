from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def http_username():
    return settings.HTTP_USERNAME


@register.simple_tag
def http_password():
    return settings.HTTP_PASSWORD
