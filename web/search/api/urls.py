from django.conf.urls import url

from web.search.api.views import *

urlpatterns = [
    url(
            regex=r'^strain',
            view=StrainSearchWizardView.as_view(),
            name='strain'
    ),
    url(
        regex=r'^strain/result/$',
        view=StrainSearchResultsView.as_view(),
        name='strain_result'
    ),
]
