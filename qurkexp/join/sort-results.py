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

num_to_compare = -1
if len(sys.argv) != 2:
    print "Arguments: at_least_comparisons"
    sys.exit()
at_least_comparisons = int(sys.argv[1])
run_names = [
#            "test-ratings-4",
#            "squares-cmp-10-1-2-5-1", # compare 10 squares, batch 1, sort size 2, 5 assignments 1 cent each
#            "squares-cmp-10-1-5-5-1", # compare 10 squares, batch 1, sort size 5, 5 assignments 1 cent each
#            "squares-cmp-10-3-5-5-1", # compare 10 squares, batch 3, sort size 5, 5 assignments 1 cent each
#            "squares-rating-10-1-1-5-1", # compare 10 squares with rating, batch 1, 5 assignments 1 cent each
#            "squares-rating-10-3-1-5-1", # compare 10 squares with rating, batch 3, 5 assignments 1 cent each
#            "squares-rating-20-5-1-5-1", # compare 20 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-25-5-1-5-1", # compare 25 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-30-5-1-5-1", # compare 30 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-35-5-1-5-1", # compare 35 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-40-5-1-5-1", # compare 40 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-45-5-1-5-1", # compare 45 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-50-5-1-5-1", # compare 50 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-cmp-40-5-5-5-1", # compare 40 squares with sorting, batch size 5, sort size 5, 5 assignments 1 cent each
#            "squares-cmp-40-5-5-5-2", # compare 40 squares with sorting, batch size 5, sort size 5, 5 assignments 1 cent each
#    "movie_cmp_1_1_5_5_v1", # compare adam's scenes with sorting, batch size 1, sort size 5, 5 assignments
    "animals-saturn-cmp-1-5-5-1"
            ]

def compare(v1, v2):
    if v1 > v2:
        return "gt"
    elif v2 > v1:
        return "lt"
    else:
        return "eq"

def sanity_check(pair_results):
    allpairs = set()
    for name in run_names:
        cvs = CompVal.objects.filter(compgroup__batch__experiment__run_name = name).distinct().order_by('-pk')
        cv_datas = []
        for cv1 in cvs:
            for cv2_data in cv_datas:
                pair = (cv1.data, cv2_data)
                if pair not in pair_results:
                    print "looked up (%d, %d)" % pair
                    for v1, v2 in pair_results.keys():
                        print "pair results has (%s, %s)" % (v1, v2)
                    raise Exception("pair_results incomplete")
                allpairs.add(pair)
            cv_datas.append(cv1.data)
    print "total pairs: ", len(allpairs)
    if len(allpairs) != len(pair_results):
        raise Exception("pair_results size is off")

    for k,v in pair_results.items():
        if len(v['answers']) < at_least_comparisons:
            raise Exception("There aren't enough comparisons of (%s, %s)" % (k[0], k[1]))
def get_sort_type():
    exps = CompExperiment.objects.filter(run_name__in = run_names)
    sort_type = None
    for exp in exps:
        if sort_type == None:
            sort_type = exp.sort_type
        if sort_type != exp.sort_type:
            raise Exception("Experiments are of different sort types")
    if sort_type == None:
        raise Exception("No experiments selected")
    return sort_type

def handle_sort():
    pair_results = {}
    cras = CompRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names) 
    for cra in cras:
        if cra.v1.id >= cra.v2.id:
            raise Exception("Answers are in the top-right triangle of matrix")
        pair = (cra.v1.data, cra.v2.data)
        res = pair_results.get(pair, {})
        ans = res.get('answers', [])
        ans.append(cra.comp)
        res['answers'] = ans
        res['actual'] = compare(cra.v1.sortval, cra.v2.sortval)
        pair_results[pair] = res
    sanity_check(pair_results)
    
    match = 0.0
    total = 0.0
    for pair, res in pair_results.items():
        v1 = pair[0]
        v2 = pair[1]
        actual = res['actual']
        ans = res['answers']
        vote = max([(ans.count(x),x) for x in ans])[1]
        print "ans: ", ans
        if vote == actual:
            match += 1
        else:
            print "Incorrect match: v1=%s, v2=%s, actual=%s, vote=%s, votes=%s" % (v1, v2, actual, vote, ans)
        total += 1
    print "Accuracy: %f / %f = %f" % (match, total, match/total)

def handle_rate():
    rating_results = {}
    rras = RateRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)
    for rra in rras:
        ans = rating_results.get(rra.val.data, [])
        ans.append(rra.rating)
        rating_results[rra.val.data] = ans
    allpairs = {}
    for name in run_names:
        cvs = CompVal.objects.filter(compgroup__batch__experiment__run_name = name).distinct().order_by('-pk')
        cv2s = []
        for cv1 in cvs:
            for cv2 in cv2s:
                pair = (cv1.data, cv2.data)
                allpairs[pair] = compare(cv1.sortval, cv2.sortval)
            cv2s.append(cv1)
    match = 0.0
    total = 0.0
    for pair, actual in allpairs.items():
        vote1 = sum(rating_results[pair[0]])*1.0/len(rating_results[pair[0]])
        vote2 = sum(rating_results[pair[1]])*1.0/len(rating_results[pair[1]])
        vote = compare(vote1, vote2)
        if vote == actual:
            match += 1
        else:
            print "Incorrect match: v1=%s, v2=%s, actual=%s, vote=%s, vote1=%s, vote2=%s" % (pair[0], pair[1], actual, vote, rating_results[pair[0]], rating_results[pair[1]])
        total += 1
    print "Accuracy: %f / %f = %f" % (match, total, match/total)



if __name__ == "__main__":
    sort_type = get_sort_type()
    
    if sort_type == "cmp":
        handle_sort()
    elif sort_type == "rating":
        handle_rate()        
    else:
        raise Exception("Unknown sort_type")



