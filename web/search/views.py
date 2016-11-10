# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from web.search.es_service import SearchElasticService
from web.search.models import Strain


class StrainSearchWizardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/wizard.html'


class StrainSearchResultView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/search/strain/search_results.html'

    def get_context_data(self, **kwargs):
        context = super(StrainSearchResultView, self).get_context_data(**kwargs)
        r = self.request

        search_criteria = r.session.get('search_criteria')
        start_from = r.GET.get('from')

        if search_criteria:
            data = SearchElasticService().query_strain_srx_score(search_criteria, 8, start_from)
            result_list = data.get('list')
            context['search_results'] = result_list
            context['search_results_total'] = data.get('total')
            return context

        return context


class StrainDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        slug_name = kwargs.get('slug_name')
        strain = Strain.objects.get(strain_slug=slug_name)
        context = super(StrainDetailView, self).get_context_data(**kwargs)
        context['strain_id'] = strain.id
        return context
