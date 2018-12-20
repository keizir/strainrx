from django import template
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from web.system.models import TopPageMetaData

register = template.Library()


@register.simple_tag(name='seo', takes_context=True)
def seo_meta_data(context, *args, **kwargs):
    """
    Return page meta data by request path

    Usage::
        {% seo as page_meta %}
    """
    key = make_template_fragment_key('page_meta', [context['request'].path])
    if cache.get(key):
        return cache.get(key)
    try:
        meta_data = TopPageMetaData.objects.get(path=context['request'].path)
        cache.set(key, meta_data, 60 * 60 * 24)
        return meta_data
    except TopPageMetaData.DoesNotExist:
        return
