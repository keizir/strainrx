# coding: utf-8
from django.shortcuts import redirect

from web.businesses.models import Business


def user_is_owner(function):
    def wrap(request, *args, **kwargs):
        business_id = kwargs.get('business_id')
        business = Business.objects.get(pk=business_id)

        if request.user.id != business.created_by.id:
            return redirect('/')

        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
