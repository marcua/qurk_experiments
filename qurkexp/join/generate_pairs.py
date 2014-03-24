#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings
#setup_environ(settings)

from qurkexp.join.models import Pair
from qurkexp.hitlayer.models import HitLayer


num_pairs = int(sys.argv[1])
run_name = sys.argv[2]
nassignments = len(sys.argv) > 3 and int(sys.argv[3]) or 5

for i in range(1,num_pairs+1):
    for j in range(1,num_pairs+1):
        p = Pair(left=i, right=j, run_name=run_name)
        p.save()
        hitid = HitLayer.get_instance().create_job("/celeb/pair/%d/" % (p.id),
                                             ('celeb', [p.id]),
                                             desc = "Look at two pictures and decide whether or not they are of the same celebrity",
                                             title = "Compare celebrity pictures",
                                             price = 0.01,
                                             nassignments = nassignments)
