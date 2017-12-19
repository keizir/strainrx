# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

import pytz

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.db.models import Count

from web.businesses.api.services import FeaturedBusinessLocationService
from web.businesses.models import Business, BusinessLocation, State, City
from web.businesses.utils import NamePaginator
from web.users.models import User
from web.analytics.models import Event

from web.analytics.service import Analytics


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
        context['timezones'] = pytz.common_timezones
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


class DispensaryInfoView(TemplateView):
    template_name = 'pages/dispensary/dispensary_info.html'

    def get_context_data(self, **kwargs):

        context = super(DispensaryInfoView, self).get_context_data(**kwargs)
        if BusinessLocation.objects.filter(state_fk__abbreviation__iexact=kwargs.get('state').lower(),
                                           city_fk__full_name_slug__iexact=kwargs.get('city_slug').lower(),
                                           slug_name__iexact=kwargs.get('slug_name').lower(),
                                           removed_date=None).exists():

            location = BusinessLocation.objects.get(state_fk__abbreviation__iexact=kwargs.get('state').lower(),
                                                    city_fk__full_name_slug__iexact=kwargs.get('city_slug').lower(),
                                                    slug_name__iexact=kwargs.get('slug_name').lower(),
                                                    removed_date=None)
            context['business_id'] = location.business.id
            context['business_name'] = location.business.name
            context['location_id'] = location.id
            context['strain_id'] = self.request.GET.get('strain_id')
            context['active_state'] = location.state_fk
            context['active_city'] = location.city_fk
            context['location'] = location
            context['meta_desc'] = location.meta_desc
            context['social_image'] = location.social_image.url if location.social_image else "https://s3.amazonaws.com/srx-prod/static/images/logo_hr.b6cd6d08fabe.png"

            # if this came from Available At on SDP, change event name
            event = "VIEW_DISP"

            if self.request.GET.get('available_at'):
                event = "VIEW_DISP_AVAIL_AT"

            Analytics.track(
                event = event, 
                user = self.request.user,
                entity_id = location.business.id
            )


        else:
            raise Http404

        return context


class DispensariesInfoView(TemplateView):
    template_name = 'pages/dispensary/dispensaries_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesInfoView, self).get_context_data(**kwargs)
        context['states'] = State.objects.filter(active=True).order_by('abbreviation')

        if self.request.user.is_authenticated():
            try:
                location = {
                    'latitude': self.request.user.geo_location.lat,
                    'longitude': self.request.user.geo_location.lng,
                    'zip_code': self.request.user.geo_location.zipcode,
                }
            except ObjectDoesNotExist:
                location = {}
        else:
            location = {}

        context['default_image_url'] = BusinessLocation.DEFAULT_IMAGE_URL
        context['featured'] = FeaturedBusinessLocationService().get_list(**location)

        return context


class DispensariesStatesView(TemplateView):
    template_name = 'pages/dispensary/dispensaries_state_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesStatesView, self).get_context_data(**kwargs)
        if State.objects.filter(abbreviation__iexact=kwargs.get('state').lower()).exists():
            active_state = State.objects.get(abbreviation__iexact=kwargs.get('state').lower())
            context['active_state'] = active_state
            cities = City.objects.filter(state=active_state).order_by('full_name')
            context['cities_paged'] = NamePaginator(cities, on='full_name', per_page=10000)
        else:
            raise Http404
        return context


class DispensariesCitiesView(TemplateView):
    template_name = 'pages/dispensary/dispensaries_city_list.html'

    def get_context_data(self, **kwargs):
        context = super(DispensariesCitiesView, self).get_context_data(**kwargs)
        if City.objects.filter(state__abbreviation__iexact=kwargs.get('state').lower(),
                               full_name_slug=kwargs.get('city_slug')).exists():

            active_state = State.objects.get(abbreviation__iexact=kwargs.get('state').lower())
            active_city = City.objects.get(state=active_state, full_name_slug=kwargs.get('city_slug'))
            context['active_state'] = active_state
            context['active_city'] = active_city
        else:
            raise Http404

        return context


class DispensaryRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('businesses:dispensaries_list')

class BusinessAnalyticsView(TemplateView):
    template_name = 'pages/business/business_analytics.html'

    def get_context_data(self, **kwargs):
        from_date = self.request.GET.get("from")
        to_date = self.request.GET.get("to")
        
        if to_date is None:
            from_date = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d") 
            from_date = datetime.strptime(from_date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
            to_date = datetime.strptime(datetime.today().strftime("%Y-%m-%d") + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        else:
            to_date = datetime.strptime(to_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")
        
        print(from_date, to_date)

        context = super(BusinessAnalyticsView, self).get_context_data(**kwargs)
        business = Business.objects.get(pk=kwargs.get('business_id'))
        context['locations'] = BusinessLocation.objects.filter(business=business, removed_date=None).order_by('id')

        # analytics

        # lookup event data
        query = Event.objects.filter(event_date__gte=from_date, event_date__lte=to_date, entity_id=kwargs.get('business_id'), event="DISP_LOOKUP").extra(select={'day': 'date( event_date )'}).values('day').annotate(count=Count('event_date')).order_by("day")
        business_lookups_data = []

        for r in query.reverse():
            business_lookups_data.append([r.get("day").strftime("%Y-%m-%d"), r.get("count")])        

        # search event data
        query = Event.objects.filter(event_date__gte=from_date, event_date__lte=to_date, entity_id=kwargs.get('business_id'), event="VIEW_DISP_AVAIL_AT").extra(select={'day': 'date( event_date )'}).values('day').annotate(count=Count('event_date')).order_by("day")
        search_data = []

        for r in query.reverse():
            search_data.append([r.get("day").strftime("%Y-%m-%d"), r.get("count")])        

        context["total_page_views"] = Event.objects.filter(entity_id=kwargs.get('business_id'), event__in=["VIEW_DISP", "VIEW_DISP_AVAIL_AT", "DISP_LOOKUP"]).count()
        context["total_calls"] = Event.objects.filter(entity_id=kwargs.get('business_id'), event="DISP_CALL").count()
        context["total_directions"] = Event.objects.filter(entity_id=kwargs.get('business_id'), event="DISP_GETDIR").count()
        context["chart_biz_lookup"] = business_lookups_data[::-1]
        context["chart_search"] = search_data[::-1]

        context['business'] = business
        context['tab'] = 'analytics'



        return context

def get_epoch_from_utc(dt):
    return int(dt.timestamp() * 1000)
