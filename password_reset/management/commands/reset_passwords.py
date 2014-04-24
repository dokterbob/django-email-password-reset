from django.core.management.base import BaseCommand

from django.template import Context
from django.template.loader import get_template

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Disable all passwords and send reset emails to all users.'

    def handle(self, *args, **options):
        # Options
        use_https = options.get('use_https', True)

        user_model = get_user_model()
        email_template = get_template('password_reset/email.txt')
        email_subject_template = get_template(
            'password_reset/email_subject.txt'
        )

        # Send password reset emails first
        email_success_users = []
        email_fail_users = []
        for user in user_model.objects.all():
           # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                self.stdout.write('Not sending email for user %s' % user)

                continue

            self.stdout.write('Sending password reset email for %s' % user)

            current_site = Site.objects.get_current()
            site_name = current_site.name
            domain = current_site.domain

            # Render message and subject
            ctx = Context({
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            })

            subject = email_subject_template.render(ctx).strip()
            message = email_template.render(ctx)

            try:
                user.email_user(subject, message)

            except Exception, e:
                self.stderr.write(
                    'Error sending password reset email for %s: %s' % (
                        user, e))

        self.stdout.write(
            'Succesfully sent %d password reset emails, %d emails failed',
            len(email_success_users), len(email_fail_users))

        # Disable existing passwords, but only for the accounts for which
        # the password reset email was succesful
        for user in email_success_users:
            user.set_unusable_password()
