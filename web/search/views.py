# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


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
        dummy_response = list()  # TODO remove this later - START

        for num in range(0, 7):
            dummy_response.append(
                {
                    'name': 'Blue Dream',
                    'type': 'Sativa',
                    'rating': '4.7',
                    'image': 'image_location.png',
                    'match_percentage': 91.45,
                    'delivery_addresses': [
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'true'
                        },
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'false'
                        },
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'false'
                        }
                    ]
                }
            )

        context['search_results'] = dummy_response
        context['search_results_total'] = 24  # TODO remove this later - END
        return context
