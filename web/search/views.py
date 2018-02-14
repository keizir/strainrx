# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from urllib.parse import urlparse

from django.core.urlresolvers import reverse, resolve, Resolver404
from django.db.models import Q
from django.http import Http404
from django.views.generic import TemplateView

from web.search.models import Strain, StrainImage


class StrainSearchWizardView(TemplateView):
    template_name = 'pages/search/strain/wizard.html'


class StrainSearchResultView(TemplateView):
    template_name = 'pages/search/strain/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sign_in_url'] = '{url}?next={next_url}'.format(
            url=reverse('account_login'),
            next_url=reverse('search:strain_results'),
        )
        return context


class StrainDetailView(TemplateView):
    template_name = 'pages/strain/strain_detail.html'

    def get_context_data(self, **kwargs):
        context = super(StrainDetailView, self).get_context_data(**kwargs)

        slug_name = kwargs.get('slug_name')
        strain_variety = kwargs.get('strain_variety')

        try:
            strain = Strain.objects.get(variety=strain_variety, strain_slug=slug_name)
        except Strain.DoesNotExist:
            raise Http404

        context['strain_id'] = strain.id
        context['strain_name'] = strain.name
        context['strain_variety'] = strain.variety
        context['social_desc'] = strain.meta_desc
        context['social_image'] = strain.social_image.url if strain.social_image else "https://s3.amazonaws.com/srx-prod/static/images/logo_hr.b6cd6d08fabe.png"
        context['from_location'] = self.get_previous_location_url()

        return context

    def get_previous_location_url(self):
        referrer = self.request.META.get('HTTP_REFERER')

        if referrer is None:
            return None

        path = urlparse(referrer).path
        try:
            match = resolve(path)
        except Resolver404:
            return None

        if match.url_name == 'dispensary_info':
            return path

        return None


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
        current_letter = kwargs.get('letter')
        paging_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                          'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        paging_letters_len = len(paging_letters)

        for i, l in enumerate(paging_letters):
            if l == current_letter:
                if i - 1 >= 0:
                    context['prev_letter'] = paging_letters[i - 1]
                if i + 1 < paging_letters_len:
                    context['next_letter'] = paging_letters[i + 1]
                break

        if current_letter == 'other':
            query = Q()
            for letter in paging_letters:
                query = query | Q(name__istartswith=letter)

            strains = Strain.objects.filter(variety=strain_variety).exclude(query).order_by('name')
            context['prev_letter'] = 'z'
        else:
            strains = Strain.objects.filter(variety=strain_variety, name__istartswith=current_letter).order_by('name')

        transformed = []
        for s in strains:
            strain_image = StrainImage.objects.filter(strain=s.id, is_approved=True)[:1]
            strain_image = strain_image[0].image.url if len(strain_image) > 0 else None
            transformed.append({'strain': s, 'strain_image': strain_image})

        context['strains'] = transformed
        context['current_letter'] = current_letter
        context['variety'] = strain_variety
        return context
