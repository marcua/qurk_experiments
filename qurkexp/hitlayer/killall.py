import os
import sys
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'

from qurkexp.hitlayer.models import *

for hit in HIT.objects.all():
    hit.kill() 
