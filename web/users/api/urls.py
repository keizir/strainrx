from django.conf.urls import url

from web.users.api.views import (
    UserDetailView,
    UserLoginView
)

urlpatterns = [
    url(
            regex=r'^(?P<user_id>\d+)/$',
            view=UserDetailView.as_view(),
            name='user-detail'
    ),
    url(
            regex=r'^login',
            view=UserLoginView.as_view(),
            name='login'
    ),
]
