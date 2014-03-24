# Calculates Sampled or unsampled Tau for cmp-rating


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


animalnames = map(lambda x: x.strip(), file('animalsort.txt', 'r').read().strip().split('\n'))


CACHE = {}
def get_compresans(run_names):
    run_names = tuple(run_names)
    if run_names in CACHE: return CACHE[run_names]
    ret = [ans for ans in CompRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)]
    CACHE[run_names] = ret
    return list(ret)
def get_rateresans(run_names):
    run_names = tuple(run_names)
    if run_names in CACHE: return CACHE[run_names]
    ret = [ans for ans in RateRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)]
    CACHE[run_names] = ret
    return list(ret)

def calculate_pi(pair_results):
    matrix = []
    for pair, answers in pair_results.items():
        random.shuffle(answers)
        smallans = answers
        pi = 0.0
        for val in ["eq", "lt", "gt"]:
            c = smallans.count(val)
            pi += c*c
        pi -= len(smallans)
        pi /= len(smallans)*(len(smallans) - 1)*1.0
        matrix.append(pi)
    return numpy.mean(matrix)


def calculate_kappa(run_names):
    sort_type = get_sort_type(run_names)
    if sort_type == "cmp":
        badkeys =  set(get_sample_keys(run_names))

        pair_results = {} # for calculating kappa (irr)
        for ans in get_compresans(run_names):
            lname, rname = ans.v1.data, ans.v2.data
            if lname in badkeys or rname in badkeys: continue

            anss = pair_results.get((lname, rname), [])
            anss.append(ans.comp)
            pair_results[(lname, rname)] = anss

        return calculate_pi(pair_results)
    elif sort_type == "rating":
        return -1
    else:
        raise Exception("unknown sort type")
    


def head_to_head(run_names):
    badkeys =  set(get_sample_keys(run_names))
    
    d = {}
    for ans in get_compresans(run_names):
        lname, rname = ans.v1.data, ans.v2.data
        if lname in badkeys or rname in badkeys: continue

        a = (ans.comp == 'lt' and -1 or ans.comp == 'gt' and 1 or 0)
        if lname < rname:
            pair = (lname, rname)
        elif lname > rname:
            pair = (rname, lname)
            a *= -1
        else: continue

        if pair not in d: d[pair] = 0
        d[pair] += a
    allpairs = d
    
    d = {}
    for ((lname, rname), comp) in allpairs.items():
        if lname not in d: d[lname] = 0
        if rname not in d: d[rname] = 0

        winner = None
        if comp < 0:
            winner = rname
        elif comp > 0:
            winner = lname
        #print "winner:", winner
        if winner != None: 
            d[winner] += 1

    wins = d.items()
    wins.sort(key=lambda x: x[1])
    #for x in wins:
    #        print animalnames[x[0]], x[0], x[1]

    return rank_ratings(dict(wins))

def all_cmp_pairs(run_names):
    d = {}
    allans = get_compresans(run_names)
    for ans in allans:
        lname, rname = int(ans.v1.data), int(ans.v2.data)
        a = (ans.comp == 'lt' and -1 or ans.comp == 'gt' and 1 or 0)

        if lname < rname:
            pair = (lname, rname)
        elif lname > rname:
            pair = (rname, lname)
            a *= -1
        else:
            continue

        if pair not in d: d[pair] = 0
        d[pair] += a
    return d

def subset_pairs(subset, allpairs):
    ret = dict()
    for x in subset:
        for y in subset:
            if x == y: continue
            pair = x < y and (x,y) or (y,x)
            if pair not in allpairs:
                print 'didnt find', pair
                continue
            ret[pair] = allpairs[pair]
    return ret

                

def compute_head_to_head(allpairs):
    d = {}
    for ((lname, rname), comp) in allpairs.items():
        if lname not in d: d[lname] = 0
        if rname not in d: d[rname] = 0

        winner = None
        if comp < 0:
            winner = rname
        elif comp > 1:
            winner = lname
        if winner != None: 
            d[winner] += 1

    wins = d.items()
    wins.sort(key=lambda x: x[1])
    # for x in wins:
    #     print animalnames[x[0]], x[0], x[1]
    return rank_ratings(dict(wins))
    
    




def get_rating_order(run_names):
    rating_results = {}
    rras = get_rateresans(run_names)
    for rra in rras:
        ans = rating_results.get(rra.val.data, [])
        ans.append(rra.rating)
        rating_results[rra.val.data] = ans

    for data, answers in rating_results.items():
        rating_results[data] = numpy.mean(answers)#Decimal(sum(answers))/Decimal(len(answers))

    ret = rating_results.items()
    ret.sort(key=lambda x:x[1])
    ret =  rank_ratings(dict(ret))


    badkeys = get_sample_keys(run_names)
    ret = dict([(key, val) for key, val in ret.items() if key not in badkeys])

    return ret

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
    return rank

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


def get_ranking(run_names):
    sort_type = get_sort_type(run_names)
    if sort_type == "cmp":
        rank = head_to_head(run_names)
    elif sort_type == "rating":
        rank = get_rating_order(run_names)
    else:
        raise Exception("unknown sort type")

    return rank

def get_sample_keys(run_names=None):
    """
    returns all the keys that the sort algorithms should IGNORE
    """
    global SHOULDSAMPLE
    if not SHOULDSAMPLE:
        return []    
    global SEED
    random.seed(SEED)
    if not run_names:
        data = map(str,range(1, len(animalnames)+1))
        random.shuffle(data)
        data = data[:len(data)-10]
        return data

    sort_type = get_sort_type(run_names)
    data = set()    
    if sort_type == "cmp":
        for ans in get_compresans(run_names):
            lname, rname = ans.v1.data, ans.v2.data
            data.add(lname)
            data.add(rname)
    elif sort_type == "rating":
        for ans in get_rateresans(run_names):
            data.add(ans.val.data)


    data = list(data)
    data.sort()
    random.shuffle(data)
    data = data[:len(data) - 10]
    return data


def align_rankings(rank1dict, rank2dict):
    if sorted(rank1dict.keys()) != sorted(rank2dict.keys()):
        print sorted(rank1dict.keys())
        print sorted(rank2dict.keys())
        raise Exception("keys of rank dictionaries don't match")
    rank1 = []
    rank2 = []
    for key in rank1dict:
        #print animalnames[key-1], '\t', rank1dict[key], '\t', rank2dict[key]
        rank1.append(rank1dict[key])
        rank2.append(rank2dict[key])


    return (rank1, rank2)
if __name__ == '__main__':
    

    tests = [('squares-cmp-40-5-5-5-2', 'squares-rating-40-10-1-5-1'),
             ('squares-cmp-40-5-5-5-2', 'squares-rating-40-5-1-5-1'),

             # ('animals-size-rating-27-5-1-5-1', 'animals-size-cmp-27-5-5-5-1'),
             #  ('animals-dangerous-cmp-27-1-5-5-1','animals-dangerous-rating-27-5-1-5-2'),
             #  ('animals-dangerous-cmp-27-5-5-5-2', 'animals-dangerous-rating-27-5-1-5-2'),
             #  ('animals-dangerous-cmp-27-1-5-5-1', 'animals-dangerous-cmp-27-5-5-5-2'),
             #  ('animals-saturn-cmp-1-5-5-1', 'animals-saturn-rating-5-1-5-1'),
             #('animals-saturn-cmp-27-1-5-5-sanity', 'animals-rating-saturn-27-5-1-5-sanity'),
             #('animals-saturn-cmp-27-1-5-5-sanity2', 'animals-rating-saturn-27-5-1-5-sanity'),
             #('animals-saturn-cmp-27-1-5-5-sanity3', 'animals-rating-saturn-27-5-1-5-sanity'),
             #(['animals-saturn-cmp-27-1-5-5-sanity2','animals-saturn-cmp-27-1-5-5-sanity'], 'animals-saturn-cmp-27-1-5-5-sanity'),
        ]
    SHOULDSAMPLE = False

    runs = [#'animals-size-cmp-27-5-5-5-1',
            #'animals-dangerous-cmp-27-1-5-5-1',
        #'animals-saturn-cmp-1-5-5-1',
        #'animals-saturn-cmp-27-1-5-5-sanity2',
        #    'animals-saturn-cmp-27-1-5-5-sanity3',        
            'animals-rating-saturn-27-5-1-5-sanity'
            #'animal-saturn-test3'
            ]

    for run in runs:
        r = get_ranking([run])
        r = sorted(r.items(), key=lambda x: x[1])
        print run, ":"
        for k,v in r:
            print animalnames[int(k)-1]
        print
    exit()
        
    

    random.seed(0)

    for runname1, runname2 in tests:
        n1 = '_'.join(str(runname1).split('-')[1:3])
        n2 = '_'.join(str(runname2).split('-')[1:3])
        name = '%s__%s' % (n1,n2)
        results = [] # tau, p

        niters = SHOULDSAMPLE and 50 or 1
        for iteridx in xrange(niters):
            SEED = random.randint(0,10000)            

            r1 = get_ranking([runname1])
            r2 = get_ranking([runname2])
            k1 = calculate_kappa([runname1])
            k2 = calculate_kappa([runname2])

            r1, r2 = align_rankings(r1, r2)
            (tau, p) = stats.kendalltau(r1, r2)
            
            #print "%d\t%s__%s\tTau = %f \t p = %f" % (iteridx, n1, n2,tau,p)
            results.append([tau, p, k1, k2])

        tmp = []
        for idx in xrange(len(results[0])):
            x = [res[idx] for res in results]
            #print stats
            tmp.append(numpy.mean(x))
            tmp.append(numpy.std(x))
            
        print "%s\t%s" % (name, ("\t%f" * len(tmp)) % tuple(tmp))
