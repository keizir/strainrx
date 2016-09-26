import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import *


class EmailService:
    def send_confirmation_email(self, user):
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        confirmation_url = settings.HOST + '/users/confirm_email/' + str(user.id)
        html_content = '<html><body><div style="font-size: 18px">To verify your email click this ' \
                       '<a href="' + confirmation_url + '">link</a>.</div></body></html>'

        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = Email(user.email)
        subject = 'StrainsRX: Verify Your Email'
        content = Content('text/html', html_content)

        mail = Mail(from_email, subject, to_email, content)
        return sg.client.mail.send.post(request_body=mail.get())
