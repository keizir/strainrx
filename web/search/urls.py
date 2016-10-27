# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^strain/wizard/$',
        view=views.StrainSearchWizardView.as_view(),
        name='strain_wizard'
    ),
    url(
        regex=r'^strain/results/$',
        view=views.StrainSearchResultView.as_view(),
        name='strain_results'
    ),
    url(
        regex=r'^strain/(?P<slug_name>.+)/$',
        view=views.StrainDetailView.as_view(),
        name='strain_detail'
    ),
]
