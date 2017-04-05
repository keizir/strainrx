# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.views.generic import TemplateView

from web.search.models import Strain


class StrainSearchWizardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard.html'


class StrainSearchResultView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/search_results.html'


class StrainDetailView(TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StrainDetailView, self).get_context_data(**kwargs)

        slug_name = kwargs.get('slug_name')
        strain_variety = kwargs.get('strain_variety')

        if Strain.objects.filter(variety=strain_variety, strain_slug=slug_name).exists():
            strain = Strain.objects.get(variety=strain_variety, strain_slug=slug_name)
            context['strain_id'] = strain.id
            context['strain_name'] = strain.name
            context['strain_variety'] = strain.variety
        else:
            raise Http404

        return context


class StrainsRootView(TemplateView):
    template_name = 'pages/strain/strains_root.html'


class StrainsSativaRootView(TemplateView):
    template_name = 'pages/strain/strains_sativa_root.html'


class StrainsIndicaRootView(TemplateView):
    template_name = 'pages/strain/strains_indica_root.html'


class StrainsHybridRootView(TemplateView):
    template_name = 'pages/strain/strains_hybrid_root.html'


class StrainsByNameView(TemplateView):
    template_name = 'pages/strain/strains_name_paged.html'

    def get_context_data(self, **kwargs):
        context = super(StrainsByNameView, self).get_context_data(**kwargs)

        strain_variety = kwargs.get('strain_variety')
        first_letter = kwargs.get('letter')

        if first_letter == '#':
            exclude_first_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                     'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            query = Q()
            for letter in exclude_first_letters:
                query = query | Q(name__istartswith=letter)

            strains = Strain.objects.filter(variety=strain_variety).exclude(query).order_by('name')
        else:
            strains = Strain.objects.filter(variety=strain_variety, name__istartswith=first_letter).order_by('name')

        context['strains'] = strains
        context['current_letter'] = first_letter
        context['variety'] = strain_variety
        return context
