# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from random import uniform

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

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
        dummy_response = list()  # TODO remove this later - START

        for num in range(0, 8):
            dummy_response.append(
                {
                    'name': 'Sour Diesel' if num % 2 == 0 else 'Amnesia Haze',
                    'type': 'Sativa',
                    'strain_slug': 'sour-diesel-flower' if num % 2 == 0 else 'amnesia-haze-flower',
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


class StrainDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        slug_name = kwargs.get('slug_name')
        strain = Strain.objects.get(strain_slug=slug_name)
        image = StrainImage.objects.filter(strain=strain)[:1]

        context = super(StrainDetailView, self).get_context_data(**kwargs)
        context['strain'] = strain
        context['strain_image'] = image[0]
        context['strain_rating'] = 4.5  # TODO check strain overall rating
        context['favorite'] = True  # TODO check user's favourites

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
