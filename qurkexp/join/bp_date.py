#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import * 
from qurkexp.hitlayer.models import HitLayer

from random import shuffle, seed

for bpe in BPExperiment.objects.all():
    bpb = bpe.bpbatch_set.all()
    if bpb.count() > 0 and bpb[0].bprespmeta_set.all().count() > 0:
        print bpe.run_name, bpe.smart_interface, bpe.bpbatch_set.all()[0].bprespmeta_set.all()[0].accept_time
