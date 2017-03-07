# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime

import pytz
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from web.businesses.models import Business, BusinessLocation
from web.users.models import User


class BusinessSignUpWizardView(TemplateView):
    template_name = 'pages/signup/b2b/wizard.html'


class BusinessSignUpDoneView(TemplateView):
    template_name = 'pages/signup/b2b/almost_done.html'


class ConfirmEmailView(TemplateView):
    template_name = 'pages/signup/b2b/email_confirmed.html'

    def get_context_data(self, **kwargs):
        uid = kwargs.get('uid')
        user = User.objects.get(pk=uid)
        user.is_email_verified = True
        user.save()
        business = Business.objects.get(created_by=user)
        business.trial_period_start_date = datetime.now()
        business.save()

        context = super(ConfirmEmailView, self).get_context_data(**kwargs)
        context['business'] = business
        return context


class BusinessDetailView(TemplateView):
    template_name = 'pages/business/business_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessDetailView, self).get_context_data(**kwargs)
        business = Business.objects.get(pk=kwargs.get('business_id'))
        context['business'] = business
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        context['timezones'] = pytz.common_timezones
        context['tab'] = 'info'
        return context


class BusinessMenuView(TemplateView):
    template_name = 'pages/business/business_menu.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessMenuView, self).get_context_data(**kwargs)
        business = Business.objects.get(pk=kwargs.get('business_id'))
        context['business'] = business
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        context['tab'] = 'menu'
        return context


class BusinessLocationsView(TemplateView):
    template_name = 'pages/business/business_locations.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessLocationsView, self).get_context_data(**kwargs)
        business = Business.objects.get(pk=kwargs.get('business_id'))
        context['business'] = business
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        context['tab'] = 'locations'
        return context


class DispensaryInfoView(TemplateView):
    template_name = 'pages/dispensary/dispensary_info.html'

    def get_context_data(self, **kwargs):
        context = super(DispensaryInfoView, self).get_context_data(**kwargs)

        if BusinessLocation.objects.filter(state__iexact=kwargs.get('state').lower(),
                                           city_slug__iexact=kwargs.get('city_slug').lower(),
                                           slug_name__iexact=kwargs.get('slug_name').lower(),
                                           removed_date=None).exists():

            location = BusinessLocation.objects.get(state__iexact=kwargs.get('state').lower(),
                                                    city_slug__iexact=kwargs.get('city_slug').lower(),
                                                    slug_name__iexact=kwargs.get('slug_name').lower(),
                                                    removed_date=None)
            context['business_id'] = location.business.id
            context['location_id'] = location.id
            context['strain_id'] = self.request.GET.get('strain_id')
        else:
            raise Http404

        return context


class DispensariesInfoView(TemplateView):
    template_name = 'pages/dispensary/dispensaries_list.html'


class DispensaryRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('businesses:dispensaries_list')
