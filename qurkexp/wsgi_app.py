#! /usr/bin/env python2.7
#import sys
import os
import django.core.handlers.wsgi
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
application = django.core.handlers.wsgi.WSGIHandler()
