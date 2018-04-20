from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from web.businesses.decorators import user_is_owner
from . import views

urlpatterns = [
    url(
        regex=r'^(\d+)/login$',
        view=views.Kiosk.display_login,
        name='login'
    ),
    url(
        regex=r'^(\d+)/start$',
        view=views.Kiosk.handle_email_redirect,
        name='login'
    ),
    url(
        regex=r'^(\d+)/dashboard',
        view=views.Kiosk.display_dashboard,
        name='dashboard'
    ),
]
