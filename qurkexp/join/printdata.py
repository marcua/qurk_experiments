#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.hitlayer.models import HitLayer
from scipy import stats


run_name = sys.argv[1]

try:
    exp = BPExperiment.objects.get(run_name=run_name)
except:
    print 'could not find run_name: ', run_name
    exit()


batches = exp.bpbatch_set.all()
for batch in batches:
    metas = batch.bprespmeta_set.all()
    for meta in metas:
        anss = meta.bprespans_set.all()
        print '\t'.join(map(str, [meta.aid, meta.wid]))

        if len(anss) == 0:
            print '\tno answers'
            continue
        for ans in anss:
            print '\t', ans.pair.left, ans.pair.right, ans.same
