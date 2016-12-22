import pytz

from django.utils import timezone


class TimezoneMiddleware(object):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated():
            tzname = user.timezone
            if tzname:
                timezone.activate(pytz.timezone(tzname))
            else:
                timezone.deactivate()

        return None
