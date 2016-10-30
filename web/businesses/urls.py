# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from web.businesses.decorators import user_is_owner
from . import views

urlpatterns = [
    url(
        regex=r'^signup/$',
        view=views.BusinessSignUpWizardView.as_view(),
        name='signup'
    ),
    url(
        regex=r'^signup/done/$',
        view=views.BusinessSignUpDoneView.as_view(),
        name='signup_done'
    ),
    url(
        regex=r'^confirm_email/(?P<uid>[0-9]{1,})/$',
        view=views.ConfirmEmailView.as_view(),
        name='confirm_email'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]{1,})/menu$',
        view=user_is_owner(views.BusinessMenuView.as_view()),
        name='menu'
    ),
]
