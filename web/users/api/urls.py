from django.conf.urls import url

from web.users.api.views import (
    UserDetailView,
    UserLoginView,
    UserSignUpWizardView,
    ResendConfirmationEmailView,
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
    url(
            regex=r'^signup',
            view=UserSignUpWizardView.as_view(),
            name='signup'
    ),
    url(
            regex=r'^resend-email-confirmation',
            view=ResendConfirmationEmailView.as_view(),
            name='resend_email_confirmation'
    ),
]
