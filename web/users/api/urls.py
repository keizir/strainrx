from django.conf.urls import url

from web.users.api.views import *

urlpatterns = [
    url(
        regex=r'^$',
        view=UsersView.as_view(),
        name='users'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/$',
        view=UserDetailView.as_view(),
        name='user-detail'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/change-pwd$',
        view=UserChangePwdView.as_view(),
        name='user_change_pwd'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/settings$',
        view=UserSettingsView.as_view(),
        name='update_setting'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/searches$',
        view=UserStrainSearchesView.as_view(),
        name='strain_searches'
    ),
    url(
        regex=r'^(?P<user_id>\d+)/reviews$',
        view=UserStrainReviewsView.as_view(),
        name='strain_reviews'
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
