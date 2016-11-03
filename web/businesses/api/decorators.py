# coding: utf-8
from rest_framework import status
from rest_framework.response import Response

from web.businesses.models import Business


def user_is_owner(function):
    def wrap(request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        filterargs = {'users__id': request.user.id, 'pk': business_id}
        businesses = Business.objects.filter(**filterargs)

        if len(businesses) == 0:
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
