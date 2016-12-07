# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.views.generic import TemplateView

from web.businesses.models import Business, BusinessLocation, BusinessLocationMenuItem
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


class BusinessDispensaryInfoView(TemplateView):
    template_name = 'pages/business/dispensary_info.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessDispensaryInfoView, self).get_context_data(**kwargs)
        business = Business.objects.get(pk=kwargs.get('business_id'))
        context['business'] = business
        locationid = BusinessLocation.objects.get(pk=kwargs.get('location_id'))
        businesslocationmenuitem = BusinessLocationMenuItem.objects.filter(business_location=locationid, removed_date=None).order_by('id')
        context['businesslocationmenuitem'] = businesslocationmenuitem
        context['businesslocation'] = locationid
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        context['tab'] = 'dispensary_info'
        return context
