# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from random import uniform

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

        for num in range(0, 8):
            dummy_response.append(
                {
                    'name': 'Blue Dream' if num % 2 == 0 else 'East Coast Sour Diesel',
                    'type': 'Sativa',
                    'rating': "{0:.2f}".format(5 * uniform(0.3, 1)),
                    'image': 'image_location.png',
                    'match_percentage': "{0:.2f}".format(100 * uniform(0.3, 1)),
                    'delivery_addresses': [
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'true',
                            'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                        },
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'false',
                            'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                        },
                        {
                            'state': 'CA',
                            'city': 'Santa Monica',
                            'street1': 'Street 1 location',
                            'open': 'false',
                            'distance': uniform(500, 3000) * 0.000621371  # meters * mile coefficient
                        }
                    ]
                }
            )

        dummy_response.sort(key=lambda entry: entry.get('match_percentage'), reverse=True)
        context['search_results'] = dummy_response
        context['search_results_total'] = 24  # TODO remove this later - END
        return context
