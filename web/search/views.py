# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from web.search.models import Strain


class StrainSearchWizardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard.html'


class StrainSearchResultView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/search_results.html'


class StrainDetailView(TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        slug_name = kwargs.get('slug_name')
        strain = Strain.objects.get(strain_slug=slug_name)
        context = super(StrainDetailView, self).get_context_data(**kwargs)
        context['strain_id'] = strain.id
        context['strain_name'] = strain.name
        return context


class StrainsRootView(TemplateView):
    template_name = 'pages/strain/strains_root.html'


class StrainsSativaRootView(TemplateView):
    template_name = 'pages/strain/strains_sativa_root.html'


class StrainsIndicaRootView(TemplateView):
    template_name = 'pages/strain/strains_indica_root.html'


class StrainsHybridRootView(TemplateView):
    template_name = 'pages/strain/strains_hybrid_root.html'
