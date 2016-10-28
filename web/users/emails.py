import sendgrid
from django.conf import settings
from django.core.urlresolvers import reverse
from sendgrid.helpers.mail import *


class EmailService:
    basic_email_subject = 'StrainRx: {0}'
    basic_email_with_link_pattern = '<html><body><div style="font-size: 18px">{text} ' \
                                    '<a href="{link_url}">link</a>.</div></body></html>'

    def send_confirmation_email(self, user):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        confirmation_url = '{host}{url}'.format(host=settings.HOST,
                                                url=reverse('users:confirm_email', kwargs={'uid': user.id}))

        html_content = self.basic_email_with_link_pattern.format(text='To verify your email click this',
                                                                 link_url=confirmation_url)

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = self.basic_email_subject.format('Verify Your Email')
        content = Content('text/html', html_content)

        m = Mail(from_email, subject, to_email, content)
        return sg.client.mail.send.post(request_body=m.get())

    def send_reset_pwd_email(self, user, token):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        reset_url = '{host}{url}?uid={uid}&t={token}'.format(host=settings.HOST, url=reverse('account_reset_password'),
                                                             uid=str(user.id), token=token)

        html_content = self.basic_email_with_link_pattern.format(text='To reset your password click this',
                                                                 link_url=reset_url)

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = self.basic_email_subject.format('Reset Your Password')
        content = Content('text/html', html_content)

        m = Mail(from_email, subject, to_email, content)
        return sg.client.mail.send.post(request_body=m.get())
