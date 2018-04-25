from __future__ import unicode_literals, absolute_import

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from rest_framework import status

from web.search.models import StrainReview, Strain, StrainRating
from web.search.serializers import StrainReviewESSerializer
from web.search.strain_es_service import StrainESService
from web.system.models import PermanentlyRemoved
from web.users.models import User


@receiver(post_save, sender=StrainReview)
def create_es_review(sender, **kwargs):
    strain_review = kwargs.get('instance')
    es_serializer = StrainReviewESSerializer(strain_review)
    data = es_serializer.data
    data['created_by'] = strain_review.created_by.id
    data['last_modified_by'] = strain_review.last_modified_by.id if strain_review.last_modified_by else None
    StrainESService().save_strain_review(data, strain_review.id, strain_review.strain.id)


@receiver(post_save, sender=Strain)
def create_es_strain(sender, **kwargs):
    strain = kwargs.get('instance')
    StrainESService().save_strain(strain)

    if User.objects.filter(email='tech+rate_bot@strainrx.co').exists():
        rate_bot = User.objects.get(email='tech+rate_bot@strainrx.co')
        if not StrainRating.objects.filter(strain=strain, created_by=rate_bot, removed_date=None).exists():
            r = StrainRating(strain=strain, created_by=rate_bot, effects=strain.effects, benefits=strain.benefits,
                             side_effects=strain.side_effects, status='pending')
            r.save()


@receiver(pre_delete, sender=Strain)
def remove_permanently(sender, instance, **kwargs):
    """
    Add record to PermanentlyRemoved model
    Update ES index
    """
    StrainESService().delete_strain(instance.pk)
    PermanentlyRemoved.objects.create(
        status=status.HTTP_410_GONE,
        url=instance.get_absolute_url()
    )
