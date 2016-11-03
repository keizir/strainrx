# -*- coding: utf-8 -*-
from django.conf.urls import url

from web.businesses.api.decorators import user_is_owner
from web.businesses.api.views import *

urlpatterns = [
    url(
        regex=r'^(?P<business_id>[1-9]+)/image',
        view=user_is_owner(BusinessImageView.as_view()),
        name='upload_business_image'
    ),
    url(
        regex=r'^(?P<business_id>[0-9]+)/info$',
        view=user_is_owner(BusinessDetailView.as_view()),
        name='detail'
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
