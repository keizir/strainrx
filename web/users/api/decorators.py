# coding: utf-8
from rest_framework import status
from rest_framework.response import Response


def user_is_owner(function):
    def wrap(request, *args, **kwargs):
        if request.user.id != int(kwargs.get('user_id')):
            return Response({'error': 'You are not authorized to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
