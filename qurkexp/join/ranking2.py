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


def compare(v1, v2):
    if v1 > v2:
        return "gt"
    elif v2 > v1:
        return "lt"
    else:
        return "eq"

def sanity_check(pair_results, run_names):
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
        if len(v) < at_least_comparisons:
            raise Exception("There aren't enough comparisons of (%s, %s)" % (k[0], k[1]))

def get_sort_type(run_names):
    exps = CompExperiment.objects.filter(run_name__in = run_names)
    sort_type = None
    if run_names[0] == "sortval":
        sort_type = "sortval"
    else:
        for exp in exps:
            if sort_type == None:
                sort_type = exp.sort_type
            if sort_type != exp.sort_type:
                raise Exception("Experiments are of different sort types")
    if sort_type == None:
        raise Exception("No experiments selected")
    return sort_type

def calculate_irr(pair_results):
    matrix = []
    first = True
    for pair, answers in pair_results.items():
        matrix.append([])
        random.shuffle(answers)
        matrix[-1].append(len([1 for ans in answers[:at_least_comparisons] if ans == "eq"]))
        matrix[-1].append(len([1 for ans in answers[:at_least_comparisons] if ans == "gt"]))
        matrix[-1].append(len([1 for ans in answers[:at_least_comparisons] if ans == "lt"]))
        matrix.append([matrix[-1][0], matrix[-1][2], matrix[-1][1]])
    return computeKappa(matrix)

def many_irrs(pair_results):
    results = []
    for i in xrange(0,20):
        results.append(calculate_irr(pair_results))
    print "irr vals: ", results 
    print "irr mean: %f" % (stats.mean(results))
    print "irr stdev: %f" % (stats.std(results))


def calculate_pi(pair_results):
    matrix = []
    for pair, answers in pair_results.items():
        random.shuffle(answers)
        smallans = answers[:at_least_comparisons]
        pi = 0.0
        for val in ["eq", "lt", "gt"]:
            c = smallans.count(val)
            pi += c*c
        pi -= len(smallans)
        pi /= len(smallans)*(len(smallans) - 1)*1.0
        matrix.append(pi)
    return stats.mean(matrix)
    

def get_sort_rank(run_names):
    print "sort rank"
    pair_results = {}
    cras = CompRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names) 
    for cra in cras:
        if cra.v1.id >= cra.v2.id:
            raise Exception("Answers are in the top-right triangle of matrix")
        pair = (cra.v1.data, cra.v2.data)
        ans = pair_results.get(pair, [])
        ans.append(cra.comp)
        pair_results[pair] = ans
    sanity_check(pair_results, run_names)


    wins = dict()
    
    for (left, right), answers in pair_results.items():
        for num, comp in [(answers.count(x), x) for x in ['lt', 'gt']]:
            if comp == 'lt':
                winner = right
            elif comp == 'gt':
                winner = left
            if winner not in wins: wins[winner] = 0
            wins[winner] += 1

    wins = wins.items()
    wins.sort(key=lambda x: x[1])
    for x in wins:
        print x
    exit()
    



    
    #many_irrs(pair_results)
    for pair, answers in pair_results.items():
        pair_results[pair] = max([(answers.count(x),x) for x in answers])[1]
        if pair_results[pair] == "lt":
            pair_results[(pair[1], pair[0])] = "gt"
        elif pair_results[pair] == "gt":
            pair_results[(pair[1], pair[0])] = "lt"
        elif pair_results[pair] == "eq":
            pair_results[(pair[1], pair[0])] = pair_results[pair]
        else:
            raise Exception("bad comparison")

    data_set = set()
    for d1, d2 in pair_results:
        data_set.add(d1)
        data_set.add(d2)
    data_list = list(data_set)
    comparison_mapping = {"lt":-1,"gt":1,"eq":0}
    def key_comparer(x,y):
        comp = pair_results[(x,y)]
        return comparison_mapping[comp] 
    ordered = sorted(data_list, cmp=key_comparer)
    
    lastdata = None
    lastrank = 0
    index = 0
    rank = {}
    for data in ordered:
        index += 1
        if lastdata == None:
            rank[data] = index
            lastdata = data
            lastrank = index
        else:
            comp = pair_results[(lastdata,data)]
            if comp == "eq":
                rank[data] = lastrank
                lastdata = data
            elif comp == "lt":
                rank[data] = index
                lastdata = data
                lastrank = index
            else:
                raise Exception("sorted values are in inconsistent order")
#        print translation_dict[data], lastrank
    return rank

def rank_ratings(rating_results):
    sortrank = sorted(rating_results.iteritems(), key=operator.itemgetter(1))
    lastval = -1
    lastrank = 0
    index = 0
    rank = {}
    for data, value in sortrank:
        index += 1
        if lastval == value:
            rank[data] = lastrank
        elif lastval < value:
            rank[data] = index
            lastrank = index
            lastval = value
        else:
            raise Exception("sorted values are in decreasing order")
#        print translation_dict[data], lastrank

    return rank

def get_rating_rank(run_names):
    print "rating rank"
    rating_results = {}
    rras = RateRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)
    for rra in rras:
        ans = rating_results.get(rra.val.data, [])
        ans.append(rra.rating)
        rating_results[rra.val.data] = ans

    for data, answers in rating_results.items():
        rating_results[data] = numpy.mean(answers)#Decimal(sum(answers))/Decimal(len(answers))
        #rating_results[data] = (numpy.mean(answers),numpy.std(answers))

    #rating_means = dict(map(lambda x: (x[0], x[1][0]), rating_results.items()))

    return rating_results

def get_sortval_rank(run_names):
    print "going sortval!"
    cvs = CompVal.objects.filter(compgroup__batch__experiment__run_name__in = run_names[1:]).distinct()
    
    rating_results = {}
    for cv in cvs:
        rating_results[cv.data] = cv.sortval

    return rank_ratings(rating_results)

def rank_ratings(rating_results):
    sortrank = sorted(rating_results.iteritems(), key=operator.itemgetter(1))
    lastval = -1
    lastrank = 0
    index = 0
    rank = {}
    for data, value in sortrank:
        index += 1
        if lastval == value:
            rank[data] = lastrank
        elif lastval < value:
            rank[data] = index
            lastrank = index
            lastval = value
        else:
            raise Exception("sorted values are in decreasing order")

def get_ranking(run_names):
    sort_type = get_sort_type(run_names)
    if sort_type == "cmp":
        rank = get_sort_rank(run_names)
    elif sort_type == "rating":
        rank = get_rating_rank(run_names)
    elif sort_type == "sortval":
        rank = get_sortval_rank(run_names)
    else:
        raise Exception("unknown sort type")

    return rank

def align_rankings(rank1dict, rank2dict):
    if sorted(rank1dict.keys()) != sorted(rank2dict.keys()):
        raise Exception("keys of rank dictionaries don't match")
    rank1 = []
    rank2 = []
    for key in rank1dict:
        rank1.append(rank1dict[key])
        rank2.append(rank2dict[key])


    return (rank1, rank2)


if __name__ == "__main__":

    # num_to_compare = -1
    # if len(sys.argv) != 2:
    #     print "Arguments: at_least_comparisons"
    #     sys.exit()
    # at_least_comparisons = int(sys.argv[1])
    # run_names1 = [
    #     'movie_cmp_4_1_5_5_v3',
    #             ]
    # run_names2 = [
    #     'movie_rat_4_5_1_5_v3',
    # ]
    # translation_dict = animals_dict
    at_least_comparisons = 5
    rank_ratings = get_ranking([sys.argv[1]])
    

    animalnames = map(lambda x: x.strip(), file('animalsort.txt', 'r').read().split('\n'))
    

    # print '<br/><html><body style="font-size:20pt">'
    # imgtmp = "http://wutang.csail.mit.edu:8000/media/images/animals/%d.jpg"
    #triples = [(k,avg,std) for k, (avg, std) in rank_ratings.items()]
    triples = [(k,avg) for k, avg in rank_ratings.items()]    
    triples.sort(lambda x,y: x[1] < y[1] and -1 or 1)
    for k, avg in triples:
        #print '<img src="%s" />%f, %f<br/>' % (imgtmp % int(k), avg, std)
        print animalnames[int(k)-1], avg
    #print '</body></html>'
    #print "STD", numpy.mean(map(lambda x: x[2], triples))
    exit()
        
    

    rank1dict = get_ranking(run_names1)
    rank2dict = get_ranking(run_names2)

    #print run_names1
    items1 = rank1dict.items()
    items1.sort(lambda x,y: x[1]<y[1] and -1 or 1)

    items2 = rank2dict.items()
    items2.sort(lambda x,y: x[1]<y[1] and -1 or 1)

    print '<html><body>'
    imgtmp = "http://wutang.csail.mit.edu:8000/media/images/scenes/%03d.jpg"    
    for (k,v), (k2, v2) in zip(items1, items2):
        print '<img src="%s" /><img src="%s"/><br/>' % (imgtmp % int(k), imgtmp % (int(k2)))
    print '</body></html>'

    
    
    (rank1, rank2) = align_rankings(rank1dict, rank2dict)

    (tau, p) = stats.kendalltau(rank1,rank2)
    print "Tau = %f, p = %f" % (tau,p)

