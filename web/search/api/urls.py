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
        regex=r'^strain/like',
        view=StrainLikeView.as_view(),
        name='strain_like'
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
