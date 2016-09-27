from django.conf.urls import url

from web.search.api.views import *

urlpatterns = [
    url(
            regex=r'^strain',
            view=StrainSearchWizardView.as_view(),
            name='strain'
    ),
]
