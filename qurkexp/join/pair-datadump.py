#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.join.gal import getbtjoindata, getjoindata, run_gal
from qurkexp.hitlayer.models import HitLayer
from scipy import stats

#batch = (sys.argv[1] == "batch")
#num_to_compare = int(sys.argv[2]) 

#run_name = "joinpairs-actual-4" # match 6x6, 5 assignments each, 1 cent
#run_name = "joinpairs-30-2" # match 30x30, 5 assignments each, 1 cent
#run_name = "joinpairs-30-5" # match 30x30, 5 assignments each, 1 cent
#run_name = "joinpairs-20-2" # match 20x20, 5 assignments each, 1 cent
#run_name = "joinpairs-20-4" # match 20x20, 5 assignments each, 1 cent
#run_name = "joinpairs-15-1" # match 15x15, 5 assignments each, 1 cent

run_groups = [
#             [False, "joinpairs-30-5",],
#             [False, "joinpairs-30-2",],
#              [False, "joinpairs-30-2", "joinpairs-30-5",],
#             [False, "joinpairs-20-2",],
#             [False, "joinpairs-20-4",],
#              [False, "joinpairs-20-2", "joinpairs-20-4",],
#             [False, "joinpairs-15-1",],
#             [True, "30-10-naive-ordered-1",], # match 30x30, batch size 10, 5 assignments each, 1 cent
#              [True, "30-10-naive-ordered-20",], # match 30x30, batch size 10, 5 assignments each, 1 cent
#              [True, "30-10-naive-ordered-1", "30-10-naive-ordered-20",],
#             [True, "30-5-naive-ordered-1",], # match 30x30, batch size 5, 5 assignments each, 1 cent
#              [True, "30-5-naive-ordered-20",], # match 30x30, batch size 5, 5 assignments each, 1 cent
#              [True, "30-5-naive-ordered-1", "30-5-naive-ordered-20",],
#             [True, "30-3-naive-ordered-1",], # match 30x30, batch size 3, 5 assignments each, 1 cent
#              [True, "30-3-naive-ordered-20",], # match 30x30, batch size 3, 5 assignments each, 1 cent
#              [True, "30-3-naive-ordered-1", "30-3-naive-ordered-20",],
#             [True, "20-1-naive-ordered-3",], # match 20x20, batch size 3, 5 assignments each, 1 cent
#             [True, "20-1-naive-ordered-4",], # match 20x20, batch size 3, 5 assignments each, 1 cent
#             [True, "20-1-naive-ordered-3", "20-1-naive-ordered-4",],
#             [True, "20-1-naive-ordered-1-ACTUALLYSMART",], # match 20x20, batch size 1, 5 assignments each, 1 cent
#             [True, "20-1-naive-ordered-2-ACTUALLYSMART",], # match 20x20, batch size 1, 5 assignments each, 1 cent
#             [True, "20-1-naive-ordered-1-ACTUALLYSMART", "20-1-naive-ordered-2-ACTUALLYSMART",],
#             [True, "8-2-smart-ordered-1",], # match 8x8, batch size 2, 5 assignments each, 1 cent (bad join interface taint?)
#             [True, "30-5-smart-ordered-1",], # match 30x30, batch size 5, 5 assignments each, 1 cent (bad join interface taint?)
#            "30-2-smart-ordered-1", # match 30x30, batch size 2, 5 assignments each, 1 cent (bad join interface taint?)
#            "20-1-smart-ordered-1", # match 20x20, batch size 1, 5 assignments each, 1 cent (bad join interface taint?)        
#             [True, "30-3-smart-ordered-1",], # match 30x30, batch size 3, 5 assignments each, 1 cent (fixed UI taint for IE8)
#             [True, "30-3-smart-ordered-2",], # match 30x30, batch size 3, 5 assignments each, 1 cent (fixed UI taint for IE8)
#             [True, "30-3-smart-ordered-1", "30-3-smart-ordered-2"],
#             [True, "20-1-smart-ordered-3",], # match 20x20, batch size 1, 5 assignments each, 1 cent (fixed UI taint for IE8)
#             [True, "30-2-smart-ordered-2",], # match 30x30, batch size 2, 5 assignments each, 1 cent (fixed UI taint for IE8)
#             [True, "30-2-smart-ordered-3",], # match 30x30, batch size 2, 5 assignments each, 1 cent (fixed UI taint for IE8)
#             [True, "30-2-smart-ordered-2", "30-2-smart-ordered-3"],
]

def main(batch, run_names):
    if batch:
        pairs = BPPair.objects.filter(bpbatch__experiment__run_name__in = run_names)
    else:
        pairs = Pair.objects.filter(run_name__in = run_names)

    #print "num pairs", pairs.count()
    #print "Turker histogram"
    turkers = {}
    for pair in pairs:
        if batch:
            resps = pair.bprespans_set.all()
        else:
            resps = pair.pairresp_set.all()
        for resp in resps:
            if batch:
                wid = resp.bprm.wid
            else:
                wid = resp.wid
            if wid not in turkers:
                turkers[wid] = []
            turkers[wid].append((pair.left, pair.right, resp.same))

    anonid = 0
    for wid, arr in turkers.items():
        for (left, right, same) in arr:
            print "%d\t%d\t%d\t%d\t%d" % (anonid, left, right, left == right, same)
        anonid += 1

if __name__ == "__main__":
    print "wid\tleft\tright\tcorrectans\tworkerans"
    for runs in run_groups:
        main(runs[0], runs[1:])
