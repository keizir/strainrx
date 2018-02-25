from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from web.businesses.decorators import user_is_owner
from . import views

urlpatterns = [
    url(
        regex=r'^login/$',
        view=views.KioskLogin.as_view(),
        name='login'
    ),
]
