from __future__ import unicode_literals, absolute_import

from django.core.urlresolvers import reverse
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework import status

from web.articles.models import Article
from web.system.models import PermanentlyRemoved


@receiver(post_delete, sender=Article)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model
    """
    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=instance.get_absolute_url()
    )


@receiver(post_save, sender=Article)
def moved_permanently(sender, instance, raw, created, **kwargs):
    """
    Add record to PermanentlyRemoved model with 301 status code
    """
    if created:
        return

    data = {
        'slug': instance.slug,
        'category_slug': instance.category.slug if instance.category else None
    }

    if instance.original_data != data:
        if instance.original_data['category_slug']:
            url = reverse('view_article', kwargs={
                'category_slug': instance.original_data['category_slug'],
                'article_slug': instance.original_data['slug']})
        else:
            url = reverse('view_page', args=(instance.original_data['slug'],))

        PermanentlyRemoved.objects.create(
            status=status.HTTP_301_MOVED_PERMANENTLY,
            url=url,
            redirect_url=instance.get_absolute_url()
        )
        instance.original_data = data
