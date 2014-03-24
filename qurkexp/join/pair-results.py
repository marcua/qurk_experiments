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
              [False, "joinpairs-30-2", "joinpairs-30-5",],
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

def update_matches(ismatch, foundtrue, fn, fp, tn, tp):
    if ismatch and foundtrue:
        tp += 1
    elif ismatch and not foundtrue:
        fn += 1
#        fn_group.append("%d_%d %d %d" % (left, right, true_count, false_count))
    elif not ismatch and foundtrue:
        fp += 1
#        fp_group.append("%d_%d %d %d" % (left, right, true_count, false_count))
    elif not ismatch and not foundtrue:
        tn += 1
    return (fn, fp, tn, tp)

def main(batch, run_names):
    if batch:
        pairs = BPPair.objects.filter(bpbatch__experiment__run_name__in = run_names)
    else:
        pairs = Pair.objects.filter(run_name__in = run_names)
#    if num_to_compare > 0:
#        pairs = pairs.filter(left__lte = num_to_compare).filter(right__lte = num_to_compare)

    print "num pairs", pairs.count()
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
                turkers[wid] = [0.0,0.0,[],[]]
#            weight = num_to_compare if (pair.left == pair.right) else 1
#            weight = 30 if (pair.left == pair.right) else 1
            turkers[wid][0] += 1#weight#1
            turkers[wid][1] += (1 if ((pair.left == pair.right) == resp.same) else 0)#*weight
            turkers[wid][2].append(resp.same)

    if batch:
        worker_resps = BPRespAns.objects.filter(bprm__wid__in = turkers.keys()).filter(bprm__batch__experiment__run_name__in = run_names).order_by('bprm__submit_time')
    else:
        worker_resps = PairResp.objects.filter(wid__in = turkers.keys()).filter(pair__run_name__in = run_names).order_by('submit_time')
    for resp in worker_resps:
        if batch:
            arr = turkers[resp.bprm.wid][3]    
        else:
            arr = turkers[resp.wid][3]    
        actualres = resp.pair.left == resp.pair.right
        if actualres:
            if resp.same == actualres:
                arr.append('a')
            else:
                arr.append('_')
        else:
            if resp.same == actualres:
                arr.append('b')
            else:
                arr.append('-')

    lturkers = list(turkers.items())
    lturkers.sort(lambda x,y: x[1][0] < y[1][0] and -1 or 1)
    for k,v in lturkers:
        #print k,v[0],v[1]/v[0], "".join(v[3])
        pass#print '%5f, %d, %s' % ((v[1]/v[0]), len(v[3]), "".join(v[3]))
    xs = [v[1]/v[0] for k,v in lturkers]
    print "len xs", len(xs)
    ys = [len(v[3]) for k,v in lturkers]
    print "len ys", len(ys)
    (s, i, r, p, std) = stats.linregress(ys,xs)
    print "regression---slope %f, intercept %f, R^2 %f, p %f" % (s, i, r*r, p)

    #print "Accuracy printout"
    pair_counts = {}
    for pair in pairs:
        counts = pair_counts.get((pair.left, pair.right), {})
        if batch:
            resps = pair.bprespans_set.all()
        else:
            resps = pair.pairresp_set.all()
        for resp in resps:
            if batch:
                wid = resp.bprm.wid
            else:
                wid = resp.wid
    #        if turkers[wid][1] / turkers[wid][0] < 0.6:
    #            continue
            if resp.same:
                counts["true_count"] = counts.get("true_count", 0) + 1
            else:
                counts["false_count"] = counts.get("false_count", 0) + 1
        pair_counts[(pair.left, pair.right)] = counts

    if batch:
        data = getbtjoindata(run_names)
        exptype = "btjoin"
    else:
        data = getjoindata(run_names)
        exptype = "join"

    gal_w, gal_res = run_gal(exptype, data)
    gal_res = dict(gal_res)

#    fp_group = []
#    fn_group = []
    (fn_mv, fp_mv, tn_mv, tp_mv, fn_g, fp_g, tn_g, tp_g) = [0.0]*8

#    tc_count = 0
    for (left, right), counts in pair_counts.items():
        (true_count, false_count) = (counts.get("true_count", 0), counts.get("false_count", 0))
        foundtrue_mv = true_count > false_count
        
        gal_dict = dict(gal_res["%d_%d" % (left, right)])
        if gal_dict["True"] > .8:
            foundtrue_g = True
        else:
            foundtrue_g = False

        ismatch = (left == right)
#        if ismatch:
#            tc_count += counts.get("true_count", 0)
        (fn_mv, fp_mv, tn_mv, tp_mv) = update_matches(ismatch, foundtrue_mv, fn_mv, fp_mv, tn_mv, tp_mv)
        (fn_g, fp_g, tn_g, tp_g) = update_matches(ismatch, foundtrue_g, fn_g, fp_g, tn_g, tp_g)
#    if not(ismatch and false_count == 0) and not(not ismatch and true_count == 0) and ismatch != foundtrue:
#        print left, right, ismatch, true_count, false_count, foundtrue

#    print "true pos, true neg, false pos, false neg"
    print "%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d" % ("+".join(run_names), fn_mv, fp_mv, tn_mv, tp_mv, fn_g, fp_g, tn_g, tp_g)
    print "tc_count", tc_count
#    fp_group.sort()
#    fn_group.sort()
    #print "fp_group", fp_group
    #print "fn_group", fn_group

if __name__ == "__main__":
    print "runs\tfn_mv\tfp_mv\ttn_mv\ttp_mv\tfn_g\tfp_g\ttn_g\ttp_g"
    for runs in run_groups:
        main(runs[0], runs[1:])
