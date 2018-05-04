from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def strain_letter_page_url(variety, letter):
    return '{0}{1}'.format(settings.HOST, reverse('search:strains_type_by_name', kwargs={
        'strain_variety': variety, 'letter': letter
    }))


@register.filter
def get_item(dictionary, item):
    return dictionary.get(item)
