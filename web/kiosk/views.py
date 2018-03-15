# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.views.generic import RedirectView, TemplateView, FormView
from django.shortcuts import render
from web.businesses.models import Business, BusinessLocation, State, City, BusinessLocationMenuUpdateRequest
from . import forms
import logging


class Kiosk(TemplateView):
    # get this loading the real business id via postgres, at least do the lookup
    def display_login(self, business_id):
        logging.getLogger(__name__).error(business_id)
        business_logo = 'images/kiosk/stubloginlogo.jpg'
        return render(self, 'kiosk/login.html',
                      {'business':
                           {'logo': business_logo,
                            'id': business_id},
                       'form': forms.KioskEmailForm})

    def display_dashboard(self, business_id):
        business = Business.objects.get(pk=business_id)
        locations = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
        return render(self, 'kiosk/dashboard.html',
                      {'business': business,
                       'locations': locations})

