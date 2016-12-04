# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.views.generic import TemplateView

from .models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'id'
    slug_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'info'
        return context


class UserFavoritesView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    template_name_suffix = '_favorites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'favorites'
        return context


class UserReviewsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    template_name_suffix = '_reviews'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'reviews'
        return context


class UserNotificationsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    template_name_suffix = '_notifications'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'notifications'
        return context


class UserProximitySettingsView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    template_name_suffix = '_proximity_settings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'proximity'
        return context


class UserChangePwdView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = 'id'
    slug_url_kwarg = 'user_id'
    template_name_suffix = '_change_pwd'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'pwd'
        return context


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'id': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'id': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(pk=self.request.user.id)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'id'
    slug_url_kwarg = 'username'


class UserSignUpWizardView(TemplateView):
    template_name = 'pages/signup/b2c/wizard.html'


class UserSignUpDoneView(TemplateView):
    template_name = 'pages/signup/b2c/almost_done.html'


class ConfirmEmailView(TemplateView):
    template_name = 'pages/signup/b2c/email_confirmed.html'

    def get_context_data(self, **kwargs):
        uid = kwargs.get('uid')

        user = User.objects.get(pk=uid)
        user.is_email_verified = True
        user.save()

        context = super(ConfirmEmailView, self).get_context_data(**kwargs)
        context['step'] = 7
        return context
