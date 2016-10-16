# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from random import uniform

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from web.search.es_service import SearchElasticService
from web.search.models import Strain, StrainImage


class StrainSearchWizard1View(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard_1.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchWizard1View, self).get_context_data(**kwargs)
        context['step'] = 1
        return context


class StrainSearchWizard2View(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard_2.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchWizard2View, self).get_context_data(**kwargs)
        context['step'] = 2
        return context


class StrainSearchWizard3View(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard_3.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchWizard3View, self).get_context_data(**kwargs)
        context['step'] = 3
        search_criteria = self.request.session['search_criteria']
        context['is_2nd_step_skipped'] = search_criteria['effects'] == 'skipped'
        return context


class StrainSearchWizard4View(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard_4.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchWizard4View, self).get_context_data(**kwargs)
        context['step'] = 4
        return context


class StrainSearchResultView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/search_results.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchResultView, self).get_context_data(**kwargs)
        r = self.request

        query_strain_name = r.GET.get('q')  # TODO remove q param form url later
        search_criteria = r.session.get('search_criteria')
        start_from = r.GET.get('from')

        if search_criteria:
            data = SearchElasticService().query_strain_srx_score(search_criteria, 8, start_from)
            result_list = data.get('list')
            result_list.sort(key=lambda entry: entry.get('match_percentage'), reverse=True)
            context['search_results'] = result_list
            context['search_results_total'] = data.get('total')
            return context

        if query_strain_name:
            data = SearchElasticService().query_strains_by_name(query_strain_name, size=8, start_from=start_from)
            result_list = data.get('list')
            result_list.sort(key=lambda entry: entry.get('match_percentage'), reverse=True)
            context['search_results'] = result_list
            context['search_results_total'] = data.get('total')
            return context

        return context


class StrainDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        slug_name = kwargs.get('slug_name')
        strain = Strain.objects.get(strain_slug=slug_name)
        image = StrainImage.objects.filter(strain=strain)[:1]

        context = super(StrainDetailView, self).get_context_data(**kwargs)
        context['strain'] = strain
        context['strain_image'] = image[0] if image else None
        context['strain_rating'] = 4.5  # TODO check strain overall rating
        context['favorite'] = True  # TODO check user's favorites

        dispensaries = []

        for num in range(0, 5):
            dispensaries.append({
                'id': num,
                'name': 'The Green Shop',
                'rating': 4.6,
                'distance': 1.3,
                'price': {
                    'gram': 100.00,
                    'eight': 20.00,
                    'quarter': 30.00,
                    'half': 54.98
                }
            })

        context['dispensaries'] = dispensaries
        return context
