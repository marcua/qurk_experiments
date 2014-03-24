import os
import sys
#print sys.path
from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
application = WSGIHandler()
