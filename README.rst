django-email-password-reset
===========================

Minimalist app disabling all passwords and sending password reset emails.

Usage
-----
1. Install app::

       pip install django-password-reset

2. Include ``password_reset`` app in ``INSTALLED_APPS``.
3. Setup password reset template in ``password_reset/email.txt`` and ``password_reset/email_subject.txt``.
4. Do a dry-run, outputting emails to the console instead of sending them::

       ./manage.py reset_passwords -n

5. Disable all passwords and send reset emails to all users with management command::

       ./manage.py reset_passwords
