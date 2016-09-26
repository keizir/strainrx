# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
            regex=r'^$',
            view=views.UserListView.as_view(),
            name='list'
    ),

    # URL pattern for the UserRedirectView
    url(
            regex=r'^~redirect/$',
            view=views.UserRedirectView.as_view(),
            name='redirect'
    ),

    # URL pattern for the ConfirmEmailView
    url(
            regex=r'^confirm_email/(?P<uid>[0-9]{1,})/$',
            view=views.ConfirmEmailView.as_view(),
            name='confirm_email'
    ),

    # URL pattern for the UserDetailView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/$',
            view=views.UserDetailView.as_view(),
            name='detail'
    ),

    # URL pattern for the UserFavouritesDetailView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/favourites$',
            view=views.UserFavouritesView.as_view(),
            name='favourites'
    ),

    # URL pattern for the UserReviewsView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/reviews',
            view=views.UserReviewsView.as_view(),
            name='reviews'
    ),

    # URL pattern for the UserSubscriptionsView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/subscriptions',
            view=views.UserSubscriptionsView.as_view(),
            name='subscriptions'
    ),

    # URL pattern for the UserProximitySettingsView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/proximity',
            view=views.UserProximitySettingsView.as_view(),
            name='proximity'
    ),

    # URL pattern for the UserChangePwdView
    url(
            regex=r'^(?P<username>[\w.@+-]+)/pwd',
            view=views.UserChangePwdView.as_view(),
            name='change_pwd'
    ),

    # URL pattern for the UserUpdateView
    url(
            regex=r'^~update/$',
            view=views.UserUpdateView.as_view(),
            name='update'
    ),

    # TODO maybe these 6 views can be merged into one
    url(
            regex=r'^signup/wizard/1/$',
            view=views.UserSignUpWizard1View.as_view(),
            name='signup1'
    ),
    url(
            regex=r'^signup/wizard/2/$',
            view=views.UserSignUpWizard2View.as_view(),
            name='signup2'
    ),
    url(
            regex=r'^signup/wizard/3/$',
            view=views.UserSignUpWizard3View.as_view(),
            name='signup3'
    ),
    url(
            regex=r'^signup/wizard/4/$',
            view=views.UserSignUpWizard4View.as_view(),
            name='signup4'
    ),
    url(
            regex=r'^signup/wizard/5/$',
            view=views.UserSignUpWizard5View.as_view(),
            name='signup5'
    ),
    url(
            regex=r'^signup/wizard/6/$',
            view=views.UserSignUpWizard6View.as_view(),
            name='signup6'
    ),
]
