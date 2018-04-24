from __future__ import unicode_literals, absolute_import

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from rest_framework import status

from web.articles.models import Article
from web.system.models import PermanentlyRemoved


@receiver(pre_delete, sender=Article)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model
    """
    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=instance.get_absolute_url()
    )
