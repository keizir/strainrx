from django.conf.urls import url

from web.search.api.views import *

urlpatterns = [
    url(
        regex=r'^effect/(?P<effect_type>[a-z_]+)$',
        view=StrainEffectView.as_view(),
        name='effect_type'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/image',
        view=StrainUploadImageView.as_view(),
        name='upload_strain_image'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/rate',
        view=StrainRateView.as_view(),
        name='strain_rate'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/details',
        view=StrainDetailsView.as_view(),
        name='strain_details'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/reviews',
        view=StrainReviewsView.as_view(),
        name='strain_reviews'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/user_reviews',
        view=StrainUserReviewsView.as_view(),
        name='strain_user_reviews'
    ),
    url(
        regex=r'^strain/(?P<strain_id>[0-9]+)/favorite',
        view=StrainFavoriteView.as_view(),
        name='strain_favorite'
    ),
    url(
        regex=r'^strain/lookup/$',
        view=StrainLookupView.as_view(),
        name='strain_lookup'
    ),
    url(
        regex=r'^strain',
        view=StrainSearchWizardView.as_view(),
        name='strain'
    ),
    url(
        regex=r'^result/$',
        view=StrainSearchResultsView.as_view(),
        name='strain_result'
    ),
]
