# Retrieves the unique worker ids for experiments
# for testing overlap between experiments


#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from decimal import Decimal
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.hitlayer.models import HitLayer
from qurkexp.join.fleiss import computeKappa
from scipy import stats

from qurkexp.join.animals import animals_dict

import operator
import random
import numpy






def get_sort(run_names):
    workers = set()
    for ca in CompRespMeta.objects.filter(batch__experiment__run_name__in=run_names):
        workers.add(ca.wid)
    return workers

def get_hist(run_names):
    workers = {}
    for ca in CompRespMeta.objects.filter(batch__experiment__run_name__in=run_names):
        if ca.wid not in workers:
            workers[ca.wid] = 0
        workers[ca.wid] += 1
    counts = sorted(workers.items(), key=lambda x: x[1], reverse=True)

    print run_names
    for w, c in counts:
        print "% 12s\t%d" % (w,c)
    print
    


get_hist(['animals-saturn-cmp-1-5-5-1'])
get_hist(['animals-saturn-cmp-27-1-5-5-sanity2'])
get_hist(['animals-saturn-cmp-27-1-5-5-sanity'])

exit()

sizes = """animals-size-cmp-27-5-5-5-1
animals-size-cmp-27-10-2-5-1
animals-size-cmp-27-2-10-5-1
animals-size-rating-27-5-1-5-1
animals-size-rating-27-10-1-5-1
animals-size-rating-27-5-1-5-2""".split("\n")


dangers = """animals-dangerous-rating-27-5-1-5-1
animals-dangerous-rating-27-5-1-5-2
animals-dangerous-cmp-27-5-5-5-2
animals-dangerous-cmp-27-1-5-5-1""".split("\n")

saturns = """animals-saturn-cmp-1-5-5-1
animals-saturn-cmp-27-1-5-5-sanity
animals-saturn-rating-5-1-5-1
animals-rating-saturn-27-5-1-5-sanity""".split("\n")

wsizes = get_sort(sizes)
wdangers = get_sort(dangers)
wsaturns = get_sort(saturns)
print len(wsizes)
print len(wdangers)
print len(wsaturns)

intersizes = wsizes.intersection(wsaturns)
interdangers = wdangers.intersection(wsaturns)

intersaturn = get_sort(['animals-saturn-cmp-27-1-5-5-sanity2']).intersection(get_sort(['animals-saturn-cmp-27-1-5-5-sanity2']))


sizeexp = CompRespMeta.objects.filter(batch__experiment__run_name__in=saturns)

print 'sizes', sizeexp.filter(wid__in=intersizes).count(), sizeexp.count()
print 'saturn', sizeexp.filter(wid__in=intersaturn).count(), sizeexp.count()
print 'danger', sizeexp.filter(wid__in=interdangers).count(), sizeexp.count()
