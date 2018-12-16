from django import template

from web.system.models import TopPageMetaData

register = template.Library()


@register.simple_tag(name='seo', takes_context=True)
def seo_meta_data(context, *args, **kwargs):
    """
    Return page meta data by request path

    Usage::
        {% seo as page_meta %}
    """
    try:
        return TopPageMetaData.objects.get(path=context['request'].path)
    except TopPageMetaData.DoesNotExist:
        return
