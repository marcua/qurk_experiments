#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.join.fleiss import computeKappa
from qurkexp.join.generate_filters import CANT_TELL

import operator

num_pairs = int(sys.argv[1])

#ground = "testfilters-batch-116" # good ground truth for 5 batched.  one natalie portman hair is can't tell
#test = "testfilters-batch-124" # good test for 5 batched.  two skins are can't tell, one is wrong.  one hair is can't tell, one is wrong.
#test = "testfilters-batch-125" # good test for 5 nobatched.  one gender is wrong, one is can't tell. two hair color is can't tell, one is wrong.
#test = "realfilters-batch-1" # 30 batched, 5 assignments each, 1 cent.
#ground = "realfilters-batch-4" # 30 batched, 5 assignments each, 1 cent.
test = "realfilters-nobatch-2" # 30 not batched, 5 assignments each, 1 cent. skin color for http://people.csail.mit.edu/marcua/experiments/join/2/15.jpg was hung on 1 of 5 assignments.  I added another and killed it manually.  There were four votes for white (656) and one for can't tell (658), which results in a correct response.
ground = "realfilters-nobatch-5" # 30 not batched, 5 assignments each, 1 cent. 


_all_features = {}
def celeb_feature_counts(celeb):
    if celeb in _all_features:
        fras = _all_features[celeb]
    else:
        fras = FeatureRespAns.objects.filter(fr__celeb = celeb)
        _all_features[celeb] = fras
    cd = {}
    for fra in fras:
        fn = fra.feature.name
        vn = fra.val.name
        feat = cd.get(fn, {})
        vc = feat.get(vn, 0)
        feat[vn] = vc + 1
        cd[fn] = feat
    return cd

def fleiss_category_counts(celeb, feature, value_labels):
    cd = celeb_feature_counts(celeb)
    counts = []
    for l in value_labels:
        try:
            counts.append(cd[feature.name].get(l, 0))
        except KeyError:
            #print "Skipping %s for %d_%d" % (feature.name, celeb.cid, celeb.image_set)
            return None
    return counts
    
def get_feature_dict(celeb):
    cd = celeb_feature_counts(celeb)
    fd = {}
    for fn, vals in cd.iteritems():
        sv = sorted(vals.iteritems(), key=operator.itemgetter(1), reverse=True)
        fd[fn] = CANT_TELL
        if len(sv) == 1:
            fd[fn] = sv[0][0]
        elif len(sv) > 1 and sv[0][1] > sv[1][1]:
            fd[fn] = sv[0][0]
    return fd

def print_feature_accuracy(gfs, tfs, fn):
    """
        prints feature accuracy betwen ground and test features for the feature
        named fn
    """
    total = 0.0
    matches = 0.0
    ct_matches = 0.0 # all matches, including "can't tell"
    for pair, gcd in gfs.iteritems():
        if pair not in tfs:
            print "Skipping %d_d: celeb not in test dataset" % pair
            continue
        tcd = tfs[pair]
        if fn not in gcd:
            print "Skipping %d_%d: gold celeb feature not found" % pair
            continue
        if fn not in tcd:
            print "Skipping %d_%d: test celeb feature not found" % pair
            continue
        total += 1
        if gcd[fn] == tcd[fn]:
            matches += 1
            ct_matches += 1
        elif gcd[fn] == CANT_TELL or tcd[fn] == CANT_TELL:
            ct_matches += 1
    print "Feature %s: total %f, accuracy %f, ct_accuracy %f" % (fn, total, matches/total, ct_matches/total)

def compare_to_gold(gfs, tfs):
    fns = (f.name for f in Feature.objects.filter(featureexperiment__run_name = ground))
    for fn in fns:
        print_feature_accuracy(gfs, tfs, fn)

def try_join(f1, f2, leave_out, keep_only):
    retval = True
    for fn in set(f1.keys()) & set(f2.keys()):
        if fn == leave_out:
            continue
        if keep_only and fn != keep_only:
            continue
        f1v = f1[fn]
        f2v = f2[fn]
        if f1v != CANT_TELL and f2v != CANT_TELL and f1v != f2v:
            retval = False
            break
    return retval

def calculate_join_groups(tfs, leave_out=None, keep_only=None):
    tp = 0.0
    tn = 0.0
    fn = 0.0
    fp = 0.0
    for i in range(1,num_pairs+1):
        for j in range(1,num_pairs+1):
            would_join = try_join(tfs[(i,1)], tfs[(j,2)], leave_out, keep_only)
            if i == j:
                if would_join:
                    tp += 1
                else:
                    fn += 1
                    print "false neg: %d" % (i), tfs[(i,1)], tfs[(j,2)]
            else:
                if would_join:
                    fp += 1
                else:
                    tn += 1
    print "tp, fp, tn, fn, %f, %f, %f, %f" % (tp, fp, tn, fn)

def print_features(features):
    line = ""
    for fn, val in features.iteritems():
        line += "%s: %s, " % (fn, val)
    print line

def print_test_features(tfs):
    for i in range(1, num_pairs+1):
        for j in [1,2]:
            print i, j
            print_features(tfs[(i,j)])

def feature_fleiss(test_name, tfcs):
    features = Feature.objects.filter(featureexperiment__run_name = test_name).order_by('order')
    feature_matrices = {}
    for f in features:
        values = FeatureVal.objects.filter(feature = f).order_by('order')
        value_labels = [v.name for v in values]
        feature_matrices[f.name] = filter(lambda x: x != None, [fleiss_category_counts(c, f, value_labels) for c in tfcs])
    for f in features:
        print "feature kappa %s: %f" % (f.name, computeKappa(feature_matrices[f.name]))

if __name__ == "__main__":
    gfcs = FeatureCeleb.objects.filter(experiment__run_name = ground)
    tfcs = FeatureCeleb.objects.filter(experiment__run_name = test)
    gfs = dict(((c.cid, c.image_set), get_feature_dict(c)) for c in gfcs)
    tfs = dict(((c.cid, c.image_set), get_feature_dict(c)) for c in tfcs)
#    print "test features"
#    print_test_features(tfs)
    print "comparing gold to test sets"
    compare_to_gold(gfs, tfs)
    print "counting pair accuracy"
    calculate_join_groups(tfs)
    print "\n"
    print "counting pair accuracy---leave out Gender"
    calculate_join_groups(tfs, leave_out="Gender")
    print "counting pair accuracy---leave out Hair Color"
    calculate_join_groups(tfs, leave_out="Hair Color")
    print "counting pair accuracy---leave out Skin Color"
    calculate_join_groups(tfs, leave_out="Skin Color")
    print "\n"
    print "counting pair accuracy---keep only Gender"
    calculate_join_groups(tfs, keep_only="Gender")
    print "counting pair accuracy---keep only Hair Color"
    calculate_join_groups(tfs, keep_only="Hair Color")
    print "counting pair accuracy---keep only Skin Color"
    calculate_join_groups(tfs, keep_only="Skin Color")

    feature_fleiss(test, tfcs)
