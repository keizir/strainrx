import pytz

from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.contrib import auth
from django.contrib.auth.middleware import AuthenticationMiddleware as DjangoAuthenticationMiddleware

from web.users.models import CustomAnonymousUser


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


def get_user(request):
    if not hasattr(request, '_cached_user'):
        user = auth.get_user(request)
        if user.is_anonymous():
            user = CustomAnonymousUser(request)

        request._cached_user = user
    return request._cached_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        request.user = SimpleLazyObject(lambda: get_user(request))
        request._user = SimpleLazyObject(lambda: get_user(request))
