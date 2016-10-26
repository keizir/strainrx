# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import TemplateView


class BusinessSignUpWizardView(TemplateView):
    template_name = 'pages/signup/b2b/wizard.html'
