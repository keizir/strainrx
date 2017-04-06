# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^search/strain/wizard/$',
        view=views.StrainSearchWizardView.as_view(),
        name='strain_wizard'
    ),
    url(
        regex=r'^search/strain/results/$',
        view=views.StrainSearchResultView.as_view(),
        name='strain_results'
    ),
    url(
        regex=r'^strains/$',
        view=views.StrainsRootView.as_view(),
        name='strains_root'
    ),
    url(
        regex=r'^strains/sativa/$',
        view=views.StrainsSativaRootView.as_view(),
        name='strains_sativa_root'
    ),
    url(
        regex=r'^strains/indica/$',
        view=views.StrainsIndicaRootView.as_view(),
        name='strains_indica_root'
    ),
    url(
        regex=r'^strains/hybrid/$',
        view=views.StrainsHybridRootView.as_view(),
        name='strains_hybrid_root'
    ),
    url(
        regex=r'^strains/(?P<strain_variety>sativa|hybrid|indica)/list/(?P<letter>[a-z]+)/$',
        view=views.StrainsByNameView.as_view(),
        name='strains_type_by_name'
    ),
    url(
        regex=r'^strains/(?P<strain_variety>sativa|hybrid|indica)/(?P<slug_name>.+)/$',
        view=views.StrainDetailView.as_view(),
        name='strain_detail'
    ),
]
