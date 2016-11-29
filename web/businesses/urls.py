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
        regex=r'^(?P<business_id>[0-9]+)/info$',
        view=user_is_owner(views.BusinessDetailView.as_view()),
        name='detail'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]{1,})/menu$',
        view=user_is_owner(views.BusinessMenuView.as_view()),
        name='menu'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]{1,})/locations$',
        view=user_is_owner(views.BusinessLocationsView.as_view()),
        name='locations'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]{1,})/locations/(?P<location_id>[0-9]{1,})/$',
        view=views.BusinessDispensaryInfoView.as_view(),
        name='dispensary_info'
    ),
]
