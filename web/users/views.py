# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.views.generic import TemplateView

from .models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'info'
        return context


class UserFavouritesView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name_suffix = '_favourites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'favourites'
        return context


class UserReviewsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name_suffix = '_reviews'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'reviews'
        return context


class UserSubscriptionsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name_suffix = '_subscriptions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'subscriptions'
        return context


class UserProximitySettingsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name_suffix = '_proximity_settings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'proximity'
        return context


class UserChangePwdView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name_suffix = '_change_pwd'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'pwd'
        return context


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserSignUpWizard1View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_1.html'

    def get_context_data(self, **kwargs):
        context = super(UserSignUpWizard1View, self).get_context_data(**kwargs)
        context['passed'] = False

        if self.request.session.get('t_val') is not None:
            token = self.request.session.get('t_val')
            user_info = self.request.session.get(str(token))

            if user_info is not None:
                context['first_name'] = user_info.get('first_name')
                context['last_name'] = user_info.get('last_name')
                context['passed'] = True
        else:
            token = str(uuid.uuid1())

        context['token'] = token
        context['step'] = 1
        self.request.session['t_val'] = token
        return context


class UserSignUpWizard2View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_2.html'

    def get_context_data(self, **kwargs):
        context = super(UserSignUpWizard2View, self).get_context_data(**kwargs)
        token = self.request.session['t_val']
        user_info = self.request.session[str(token)]
        context['token'] = token
        context['step'] = 2
        context['passed'] = False
        is_age_verified = user_info.get('is_age_verified')

        if is_age_verified is not None:
            context['is_age_verified'] = is_age_verified
            context['passed'] = True

        self.request.session['t_val'] = token
        return context


class UserSignUpWizard3View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_3.html'

    def get_context_data(self, **kwargs):
        context = super(UserSignUpWizard3View, self).get_context_data(**kwargs)
        token = self.request.session['t_val']
        user_info = self.request.session[str(token)]
        context['token'] = token
        context['step'] = 3
        context['passed'] = False

        email = user_info.get('email')
        if email is not None:
            context['email'] = email
            context['passed'] = True

        self.request.session['t_val'] = token
        return context


class UserSignUpWizard4View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_4.html'

    def get_context_data(self, **kwargs):
        token = self.request.session['t_val']
        context = super(UserSignUpWizard4View, self).get_context_data(**kwargs)
        context['token'] = token
        context['step'] = 4
        self.request.session['t_val'] = token
        return context


class UserSignUpWizard5View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_5.html'

    def get_context_data(self, **kwargs):
        token = self.request.session['t_val']
        context = super(UserSignUpWizard5View, self).get_context_data(**kwargs)
        context['token'] = token
        context['step'] = 5
        self.request.session['t_val'] = token
        return context


class UserSignUpWizard6View(TemplateView):
    template_name = 'pages/signup/b2c/wizard_6.html'

    def get_context_data(self, **kwargs):
        context = super(UserSignUpWizard6View, self).get_context_data(**kwargs)
        context['step'] = 6
        return context


class ConfirmEmailView(TemplateView):
    template_name = 'pages/signup/b2c/wizard_7.html'

    def get_context_data(self, **kwargs):
        uid = kwargs.get('uid')

        user = User.objects.get(pk=uid)
        user.is_email_verified = True
        user.save()

        context = super(ConfirmEmailView, self).get_context_data(**kwargs)
        context['step'] = 7
        return context
