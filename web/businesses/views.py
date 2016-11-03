# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.views.generic import TemplateView

from web.businesses.models import Business
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
        context['tab'] = 'info'
        context['business'] = business
        return context


class BusinessMenuView(TemplateView):
    template_name = 'pages/business/business_menu.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessMenuView, self).get_context_data(**kwargs)
        context['tab'] = 'menu'
        return context


class BusinessLocationsView(TemplateView):
    template_name = 'pages/business/business_locations.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessLocationsView, self).get_context_data(**kwargs)
        context['tab'] = 'locations'
        return context


class BusinessBillingInfoView(TemplateView):
    template_name = 'pages/business/business_billing_info.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessBillingInfoView, self).get_context_data(**kwargs)
        context['tab'] = 'billing'
        return context


class BusinessDeliveryRadiusView(TemplateView):
    template_name = 'pages/business/business_delivery_radius.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessDeliveryRadiusView, self).get_context_data(**kwargs)
        context['tab'] = 'radius'
        return context


class BusinessChangePwdView(TemplateView):
    template_name = 'pages/business/business_change_pwd.html'

    def get_context_data(self, **kwargs):
        context = super(BusinessChangePwdView, self).get_context_data(**kwargs)
        context['tab'] = 'pwd'
        return context
