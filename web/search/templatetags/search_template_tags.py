from django import template

register = template.Library()


@register.simple_tag
def find_closest_delivery_distance(array):
    distances = []
    for dispensary in array:
        distances.append(dispensary.get('distance'))

    min_distance = min(distances)
    min_distance = "{0:.2f}".format(min_distance)
    return 'Nearest ' + str(min_distance) + 'mi'


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

    return str(len(opened)) + ' Open, ' + str(len(closed)) + ' Close'