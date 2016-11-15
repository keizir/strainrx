# -*- coding: utf-8 -*-
from django.conf.urls import url

from web.businesses.api.views import *

urlpatterns = [
    url(
        regex=r'^(?P<business_id>[0-9]+)/image',
        view=BusinessImageView.as_view(),
        name='upload_business_image'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]+)/locations/(?P<business_location_id>[0-9]+)/menu',
        view=BusinessLocationMenuView.as_view(),
        name='business_location_menu'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]+)/locations/(?P<business_location_id>[0-9]+)',
        view=BusinessLocationView.as_view(),
        name='business_location'
    ),
    url(
        regex=r'^signup',
        view=BusinessSignUpWizardView.as_view(),
        name='signup'
    ),
    url(
        regex=r'^resend-email-confirmation',
        view=ResendConfirmationEmailView.as_view(),
        name='resend_email_confirmation'
    ),
]
