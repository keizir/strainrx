# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.views.generic import RedirectView, TemplateView, FormView
from django.shortcuts import render
from . import forms
import logging


class KioskLogin(TemplateView):

    def display_kiosk_business(self, business_id):
        logging.getLogger(__name__).error(business_id)
        business_logo = 'images/kiosk/stubloginlogo.jpg'
        return render(self, 'kiosk/login.html',
                      {'business':
                           {'logo': business_logo,
                            'id': business_id},
                       'form': forms.KioskEmailForm})
