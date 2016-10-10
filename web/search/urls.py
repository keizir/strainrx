# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # TODO maybe these 4 views can be merged into one
    url(
        regex=r'^strain/wizard/1/$',
        view=views.StrainSearchWizard1View.as_view(),
        name='strain1'
    ),
    url(
        regex=r'^strain/wizard/2/$',
        view=views.StrainSearchWizard2View.as_view(),
        name='strain2'
    ),
    url(
        regex=r'^strain/wizard/3/$',
        view=views.StrainSearchWizard3View.as_view(),
        name='strain3'
    ),
    url(
        regex=r'^strain/wizard/4/$',
        view=views.StrainSearchWizard4View.as_view(),
        name='strain4'
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
