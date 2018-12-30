from __future__ import unicode_literals, absolute_import

from django.db import models


class UserSearchQuerySet(models.QuerySet):

    def user_criteria(self, user):
        return self.filter(user=user, user__display_search_history=True).order_by('-last_modified_date').first()


class StrainImageQuerySet(models.QuerySet):

    def get_images(self):
        return self.filter(is_approved=True)\
            .exclude(models.Q(image__isnull=True) | models.Q(image=''))\
            .order_by('-is_primary')
