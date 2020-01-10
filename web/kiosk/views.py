# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.views.generic import RedirectView, TemplateView, FormView
from django.shortcuts import render
from web.businesses.models import Business, BusinessLocation, State, City, BusinessLocationMenuUpdateRequest
from django.http import HttpResponseRedirect
from . import forms


def get_business(business_id):
    business = Business.objects.get(pk=business_id)
    business.locations = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')
    business.image = 'images/kiosk/stubloginlogo.jpg'
    return business


class Kiosk(TemplateView):
    def handle_email_redirect(self, business_id):
        print(self.POST.get('email', False))
        return HttpResponseRedirect('/kiosk/' + business_id + '/dashboard')

    # get this loading the real business id via postgres, at least do the lookup
    def display_login(self, business_id):
        business = get_business(business_id)
        print(business)
        return render(self, 'kiosk/login.html',
                      {'business': business,
                       'form': forms.KioskEmailForm})

    def display_dashboard(self, business_id):
        business = get_business(business_id)
        return render(self, 'kiosk/dashboard.html',
                      {'business': business})
