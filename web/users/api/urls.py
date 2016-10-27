from django.conf.urls import url

from web.users.api.decorators import user_is_owner
from web.users.api.views import *

urlpatterns = [
    url(
        regex=r'^(?P<user_id>\d+)/$',
        view=user_is_owner(UserDetailView.as_view()),
        name='user-detail'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/change-pwd$',
        view=user_is_owner(UserChangePwdView.as_view()),
        name='user_change_pwd'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/settings$',
        view=user_is_owner(UserSettingsView.as_view()),
        name='update_setting'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/searches$',
        view=user_is_owner(UserStrainSearchesView.as_view()),
        name='strain_searches'
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
    url(
        regex=r'^reset-password',
        view=ResetPasswordView.as_view(),
        name='reset_password'
    ),
]
