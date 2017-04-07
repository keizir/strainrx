from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def find_closest_delivery_distance(array):
    distances = []
    for dispensary in array:
        distances.append(dispensary.get('distance'))

    if len(distances) > 0:
        min_distance = min(distances)
        min_distance = "{0:.2f}".format(min_distance)
        return 'Nearest ' + str(min_distance) + 'mi'
    else:
        return 'No dispensaries found'


@register.simple_tag
def count_open_close_deliveries(array):
    opened = []
    closed = []
    for dispensary in array:
        is_opened = dispensary.get('open')
        if is_opened == 'true':
            opened.append(dispensary)
        elif is_opened == 'false':
            closed.append(dispensary)

    return str(len(opened)) + ' Open, ' + str(len(closed)) + ' Closed'


@register.simple_tag
def abbreviate_strain_name(origin_name):
    words = origin_name.split()
    abbreviation = ''

    if len(words) == 1:
        abbreviation = origin_name[:2]
    else:
        for word in words:
            abbreviation += word[:1].upper()

    return abbreviation


@register.simple_tag
def strain_letter_page_url(variety, letter):
    return '{0}{1}'.format(settings.HOST, reverse('search:strains_type_by_name', kwargs={
        'strain_variety': variety, 'letter': letter
    }))
