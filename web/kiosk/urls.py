from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from web.businesses.decorators import user_is_owner
from . import views

urlpatterns = [
    url(
        regex=r'^(\d+)/login$',
        view=views.KioskLogin.display_kiosk_business,
        name='login'
    ),
]
