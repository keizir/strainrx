from django.contrib.postgres.fields import JSONField
from web.users.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from web.users.models import User

@python_2_unicode_compatible
class Event(models.Model):
    event = models.CharField(max_length=24, blank=False, null=False, db_index=True)
    entity_id = models.IntegerField(blank=False, null=False)
    user = models.ForeignKey(User, blank=True, null=True)
    event_date = models.DateTimeField(default=timezone.now, db_index=True)
    properties = JSONField()
