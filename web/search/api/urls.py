from django.conf.urls import url

from web.search.api.views import *

urlpatterns = [
    url(
        regex=r'^strain/(?P<strain_id>[1-9]+)/image',
        view=StrainUploadImageView.as_view(),
        name='upload_strain_image'
    ),
    url(
        regex=r'^strain/like',
        view=StrainLikeView.as_view(),
        name='strain_like'
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
