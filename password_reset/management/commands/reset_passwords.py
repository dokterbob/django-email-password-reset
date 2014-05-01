from optparse import make_option

from django.core.management.base import BaseCommand

from django.template import Context
from django.template.loader import get_template

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site

from django.test.utils import override_settings


class Command(BaseCommand):
    help = 'Disable all passwords and send reset emails to all users.'

    option_list = BaseCommand.option_list + (
        make_option(
            '-n', '--dry-run',
            action='store_true', dest='dry_run', default=False,
            help='Dry run: send emails to console, don\'t deactivate passwords.'
        ),
    )

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
        for user in user_model.objects.exclude(email=''):
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
                if options['dry_run']:
                    # Force console email backend
                    with override_settings(
                        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
                    ):
                        user.email_user(subject, message)
                else:
                    user.email_user(subject, message)

                email_success_users.append(user)

            except Exception, e:
                self.stderr.write(
                    'Error sending password reset email for %s: %s' % (
                        user, e))

                email_fail_users.append(user)

        self.stdout.write(
            'Succesfully sent %d password reset emails, %d emails failed, '
            'skipped %d users without email addresses' % (
                len(email_success_users), len(email_fail_users),
                user_model.objects.filter(email='').count()
            )
        )

        # Disable existing passwords, but only for the accounts for which
        # the password reset email was succesful
        if options['dry_run']:
            self.stdout.write('Dry-run; not deactivating passwords.')
        else:
            self.stdout.write('Deactivating passwords for emailed users.')

            for user in email_success_users:
                user.set_unusable_password()
