# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from web.businesses.decorators import user_is_owner, authorized_for_signup
from . import views


urlpatterns = [
    url(
        regex=r'^businesses/signup/$',
        view=authorized_for_signup(views.BusinessSignUpWizardView.as_view()),
        name='signup'
    ),
    url(
        regex=r'^businesses/signup/done/$',
        view=views.BusinessSignUpDoneView.as_view(),
        name='signup_done'
    ),
    url(
        regex=r'^businesses/confirm_email/(?P<uid>[0-9]{1,})/$',
        view=views.ConfirmEmailView.as_view(),
        name='confirm_email'
    ),
    url(
        regex=r'^businesses/(?P<business_id>[0-9]+)/info/$',
        view=user_is_owner(views.BusinessDetailView.as_view()),
        name='detail'
    ),
    url(
        regex=r'^businesses/(?P<business_id>[0-9]{1,})/menu/$',
        view=user_is_owner(views.BusinessMenuView.as_view()),
        name='menu'
    ),
    url(
        regex=r'^businesses/(?P<business_id>[0-9]{1,})/partnerships/$',
        view=user_is_owner(views.BusinessPartnershipsView.as_view()),
        name='partnerships'
    ),
    url(
        regex=r'^businesses/(?P<business_id>[0-9]{1,})/locations/$',
        view=user_is_owner(views.BusinessLocationsView.as_view()),
        name='locations'
    ),
    url(
        regex=r'^dispensary/$',
        view=views.DispensaryRedirectView.as_view(),
        name='dispensary_redirect_view'
    ),
    url(
        regex=r'^dispensaries/(?P<state>.+)/(?P<city_slug>.+)/(?P<slug_name>.+)/$',
        view=views.DispensaryInfoView.as_view(),
        name='dispensary_info'
    ),
    url(
        regex=r'^dispensaries/(?P<state>.+)/(?P<city_slug>.+)/$',
        view=views.DispensariesCitiesView.as_view(),
        name='dispensaries_city_list'
    ),
    url(
        regex=r'^dispensaries/(?P<state>.+)/$',
        view=views.DispensariesStatesView.as_view(),
        name='dispensaries_state_list'
    ),
    url(
        regex=r'^dispensaries/$',
        view=views.DispensariesInfoView.as_view(),
        name='dispensaries_list'
    ),
    url(
        regex=r'^growers/$',
        view=views.GrowersInfoView.as_view(),
        name='growers_list'
    ),
    url(
        regex=r'^growers/(?P<state>.+)/(?P<city_slug>.+)/(?P<slug_name>.+)/$',
        view=views.GrowerInfoView.as_view(),
        name='grower_info'
    ),
    url(
        regex=r'^growers/(?P<state>.+)/(?P<city_slug>.+)/$',
        view=views.GrowersCitiesView.as_view(),
        name='growers_city_list'
    ),
    url(
        regex=r'^growers/(?P<state>.+)/$',
        view=views.GrowersStatesView.as_view(),
        name='growers_state_list'
    ),
    url(
        regex=r'^businesses/(?P<business_id>[0-9]{1,})/analytics/$',
        view=user_is_owner(views.BusinessAnalyticsView.as_view()),
        name='analytics'
    ),

]
