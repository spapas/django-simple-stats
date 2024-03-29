#!/usr/bin/env python

# Adapted from https://raw.githubusercontent.com/hzy/django-polarize/master/runtests.py
# and https://raw.githubusercontent.com/funkybob/django-nap/master/runtests.py

import sys

from django.conf import settings
from django.core.management import execute_from_command_line

import django


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=(
            'tests',
        ),
        MIDDLEWARE_CLASSES=[],
        DEFAULT_AUTO_FIELD='django.db.models.AutoField',
        # ROOT_URLCONF='tests.urls',
        STATIC_URL='/static/',
    )


def runtests():
    argv = sys.argv[:1] + ['test', 'tests']
    execute_from_command_line(argv)


if __name__ == '__main__':
    runtests()
