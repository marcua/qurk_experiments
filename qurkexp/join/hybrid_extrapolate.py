#!/usr/bin/env python
import sys, os, numpy, random
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import * 
#setup_environ(settings)
from scipy import stats
from test import align_rankings, rank_ratings, all_cmp_pairs, subset_pairs, compute_head_to_head



def get_rand_ratings(run_names):
    rating_results = {}
    rras = RateRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)
    datas = set()
    for rra in rras:
        datas.add(rra.val.data)

    triples = [[data, 0, 0, []] for data in datas]

    random.seed(1)
    random.shuffle(triples)
    
    for idx, trip in enumerate(triples):
        trip.append(idx)
    
    return triples


def get_comps(run_names):
    ranks = sorted(get_sort_rank(run_names).items(), lambda x,y: x[1]<y[1] and -1 or 1)
    triples = [[int(data), 0, 0, []] for data in ranks]
    for idx, trip in enumerate(triples):
        trip.append(idx)
    return triples
    
        


def get_ratings(run_names):
    rating_results = {}
    rras = RateRespAns.objects.filter(crm__batch__experiment__run_name__in = run_names)
    for rra in rras:
        ans = rating_results.get(rra.val.data, [])
        ans.append(rra.rating)
        rating_results[rra.val.data] = ans

    triples = [[int(data), numpy.mean(answers), numpy.std(answers) + 0.0001, answers]
               for data, answers in rating_results.items()]

    triples.sort(key=lambda x: x[1])

    for idx, trip in enumerate(triples):
        trip.append(idx)
    
    return triples



def maxstd_ranges(ratings):
    rating = max(ratings, key=lambda x: x[2])
    idx = rating[-1]
    minidx, maxidx = max(idx-2,0), min(len(ratings), idx+2)
    if minidx == 0:
        maxidx = min(len(ratings), 0+WINDOW)
    if maxidx == len(ratings):
        minidx = max(0, len(ratings)-WINDOW)
    subset = ratings[minidx:maxidx]
    return reorder(ratings, subset)

def std_ranges(ratings):
    bystd = sorted(ratings, lambda x,y: x[2] < y[2] and 1 or -1)
    subset = bystd[:WINDOW]

    subset = filter(lambda x: ratings[x] in subset, range(len(ratings)))
    subset = map(lambda x: ratings[x], subset)
    
    return reorder(ratings, subset)

def random_ranges(ratings):
    idxs = range(len(ratings))
    random.shuffle(idxs)
    subset = idxs[:WINDOW]
    subset = filter(lambda x: x in subset, range(len(ratings)))
    subset = map(lambda x: ratings[x], subset)

    return reorder(ratings, subset)

def farpairs_ranges(ratings):
    pairs = []
    for i in xrange(len(ratings)):
        for j in xrange(len(ratings)):
            dist = abs(i-j)
            std1 = ratings[i][2]
            avg1 = ratings[i][1]
            std2 = ratings[j][2]
            avg2 = ratings[j][1]

            if (avg1 + std1 > avg2 - std2 and avg1 + std1 <= avg2 + std2) or \
               (avg2 + std2 > avg1 - std1 and avg2 + std2 <= avg1 + std1):
                pairs.append([i, j, dist])
    pairs.sort(lambda x,y: x[2] < y[2] and -1 or 1)
    pairs = map(lambda x: x[:1], pairs)
    idxs = []
    for p in pairs:
        idxs.extend(p)
    subset = set()
    while len(idxs) > 0 and len(subset) < WINDOW:
        subset.add(idxs.pop())
    
    subset = filter(lambda x: x in subset, range(len(ratings)))
    subset = map(lambda x: ratings[x], subset)
            
    return reorder(ratings, subset)

class RandBag(object):
    def __init__(self, ratings):
        self.bag = []

    def get_func(self):
        def f(ratings):
            if len(self.bag) == 0:
                self.bag = range(len(ratings))
                random.shuffle(self.bag)

            subset = []
            while len(self.bag) > 0 and len(subset) < WINDOW:
                subset.append(self.bag.pop())

            subset = filter(lambda x: x in subset, range(len(ratings)))
            subset = map(lambda x: ratings[x], subset)

            return reorder(ratings, subset)
        return f
        

class ConfidenceWindow(object):
    def __init__(self, ratings):
        scores = [(i, self.score(ratings[i:i+WINDOW])) for i in xrange(len(ratings)-WINDOW)]
        scores.sort(lambda x,y: x[1] < y[1] and 1 or -1)
        self.windows = [map(lambda r: r[0], ratings[i:i+WINDOW]) for i, score in scores]
        self.widx = 0
        

    def score(self, l):
        ret = 0.0
        for i in xrange(len(l)):
            for j in xrange(i+1, len(l), 1):
                ret += max(0.0,(l[i][0] + l[i][2]) - (l[j][0]-l[j][2]))
        return ret

    def get_func(self):
        def f(rr):
            w = self.windows[self.widx]
            self.widx = (self.widx + 1) % len(self.windows)

            subset = w

            subset = filter(lambda i: rr[i][0] in subset, range(len(rr)))
            subset = map(lambda i: rr[i], subset)

            return reorder(rr, subset)
        return f
            


class PriorityWindow(object):
    def __init__(self, ratings, threshold=0.001):
        ratings = map(lambda x: [x[0], x[1], x[-1]], ratings)
        self.ratingsorig = list(ratings)
        self.ratings = list(ratings)
        self.threshold = threshold

        ranges = []
        while len(ratings) > 0:
            bestmin, bestmax = None, None
            idx = 0
            while idx < len(ratings):
                minidx, maxidx = self.get_interval(idx, ratings)
                if bestmin == None or (bestmax - bestmin < maxidx - minidx):
                    bestmin, bestmax = minidx, maxidx
                idx = maxidx
            extract = ratings[bestmin:bestmax]
            if len(extract) > 1:
                ranges.append((extract[0][-1], extract[-1][-1]))
                #print ranges[-1], extract[0][1], extract[-1][1]
            # remove the range 
            newratings = ratings[:bestmin]
            newratings.extend(ratings[bestmax:])
            ratings = newratings
        self.ranges = ranges
        #print "converting"

        # convert ranges to windows of size WINDOW
        windows = []
        for r in ranges:
            nitems = r[1] - r[0]
            skip = 3
            idx = 0
            first = True
            while True:
                if not first and idx % nitems == 0: break

                windows.append(set(map(lambda x: r[0] + ((x + idx) % nitems), range(WINDOW))))
                idx += skip
                idx %= nitems
                first = False
                #print windows[-1]
                
            
        self.windows = windows
        self.widx = 0
        

    def get_interval(self, idx, ratings):
        minidx, maxidx = idx, idx

        while maxidx < len(ratings) - 1:
            #print '\texpand', maxidx+1, ratings[maxidx][1], ratings[maxidx+1][1]-ratings[maxidx][1]
            if abs(ratings[maxidx+1][1] - ratings[maxidx][1]) < self.threshold:
                maxidx += 1
            else:
                break
        # +1 compensates for array slicing
        return minidx, maxidx+1


    def get_func(self):
        def f(rr):
            w = self.windows[self.widx]
            self.widx = (self.widx + 1) % len(self.windows)

            subset = [self.ratings[x] for x in w]
            subset = map(lambda x: x[0], subset)

            subset = filter(lambda i: rr[i][0] in subset, range(len(rr)))
            subset = map(lambda i: rr[i], subset)

            return reorder(rr, subset)
        return f

    

class Window(object):
    def __init__(self, skip):
        self.prev_idx = 0
        self.skip = skip
        
    def make_window_ranges(self):
        def window_ranges(ratings):
            subset = ratings[self.prev_idx: self.prev_idx + WINDOW]
            self.prev_idx += self.skip
            self.prev_idx %= len(ratings)
            return reorder(ratings, subset)
        return window_ranges

# gold = data -> index
def reorder(ratings, subset):
    global gold
    global allcmppairs
    mygold = gold

    ratings = list(ratings)
    if not mygold:
        mygold = map(lambda x: (x[1][0], x[0]),
                   enumerate(sorted(subset, lambda x,y: x[0]<y[0] and -1 or 1)))
        mygold = dict(mygold)
    else:
        mygold = subset_pairs(map(lambda x: x[0], subset), allcmppairs)
        mygold = compute_head_to_head(mygold)


    fixed = list(subset)
    fixed.sort(lambda x,y: mygold[x[0]] < mygold[y[0]] and -1 or 1)
    fixedidxs = []
    oldidxs = map(lambda x: x[-1], subset)


    ratingvals = map(lambda x:x[0], ratings)
    for r in fixed:
        fixedidxs.append(ratingvals.index(r[0]))

    #print fixedidxs, oldidxs
    
    newratings = list(ratings)
    for i, newidx in enumerate(fixedidxs):
        newratings[oldidxs[i]] = ratings[newidx]
        newratings[oldidxs[i]][2] = 0

    for idx, rate in enumerate(newratings):
        rate[-1] = idx

    return newratings



results = []

def get_tau(ratings):
    global gold
    if not gold:
        perfect = sorted(map(lambda x: x[0], ratings))
    else:
        perfect = sorted(gold.items(), key=lambda x: x[1])
        perfect = map(lambda x: x[0], perfect)
        # perfect = dict([(v,i) for i,v in enumerate(perfect)])
    rankings = map(lambda x: x[0], ratings)

    perfect = dict(map(lambda x: (x[1],x[0]), enumerate(perfect)))
    rankings = dict(map(lambda x: (x[1],x[0]), enumerate(rankings))    )
    left, right = align_rankings(perfect, rankings)
        
    (tau, p) = stats.kendalltau(left, right)
    #print "Tau = %f, p = %f" % (tau,p)
    global results
    if len(results) > 0:
        results[-1].append(tau)


def print_matrix(results):
    trans = [[0] * len(results) for i in xrange(len(results[0])) ]
    for i in xrange(len(results)):
        for j in xrange(len(results[0])):
            trans[j][i] = results[i][j]

    for i, row in enumerate(trans):
        row.insert(0, i)
        print '\t'.join(map(str, row))

def get_gold(gold_name):
    from test import head_to_head
    ret = head_to_head([gold_name])
    return ret


def get_sample(ratings, sampsize):
    idxs = range(len(ratings))
    random.shuffle(idxs)
    idxs = idxs[:sampsize]
    ret = [list(rating) for idx, rating in enumerate(ratings) if idx in idxs]
    for idx, rating in enumerate(ret):
        ret[idx][-1] = idx
    return ret




if __name__ == '__main__':
    random.seed(0)

    WINDOW = 5

    if len(sys.argv) < 3:
        print 'hybrid.py gold_cmp_runname [list of runs]'
        exit()

    gold_name = sys.argv[1]
    run_names = sys.argv[2:]
    get_data = get_ratings
    # gold_base = []
    # gold_base = get_gold(gold_name)
    # gold_base = dict([(int(k), v) for k,v in gold_base.items()])

    results = []
    names = []
    for sample_size in xrange(5, 41, 5):
        nlines = len(range(2,10))
        
        for WINDOW in xrange(2, 10):
            names.append('w%d_s%d' % (WINDOW, sample_size))
            iter_results = []
            for iteration in xrange(10):

                results.append([])
                f = Window(WINDOW-1).make_window_ranges()
                ratings = get_data(run_names)
                ratings = get_sample(ratings, sample_size)
                # gold = get_gold(gold_name)
                # gold = dict([(int(k), v) for k,v in gold.items()])
                # gold = dict([(key[0], gold[key[0]]) for key in ratings])
                # gold = dict([(k, idx) for idx, k in enumerate([x[0] for x in sorted(gold.items(), key=lambda x: x[1])])])

                # set to None if using squares dataset
                gold = None
            
                for i in xrange(80):
                    ratings = f(ratings)
                    get_tau(ratings)

                taus = results.pop()
                iter_results.append(taus)

            # average each iteration across the runs
            avg_taus = []
            std_taus = []
            for idx in xrange(len(iter_results[0])):
                vals = [iter_results[rowidx][idx] for rowidx in xrange(len(iter_results))]
                avg_taus.append(numpy.mean(vals))
                std_taus.append(numpy.std(vals)) 
            results.append(avg_taus)
            # print names[-1],avg_taus
            # print names[-1],std_taus
            # print
            
        x = range(len(results[0]))
        # import matplotlib.pyplot as plt
        # import numpy as np


        # markers = ['-', '--', '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
        # colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        # for idx, row in enumerate(results[-nlines:]):
        #     line = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
        #     plt.plot(np.array(x), np.array(row), line, label=names[idx])
        # plt.legend()
        # plt.savefig('figs/samplesize_%d.png' % sample_size, format='png')
        # plt.cla()        
        # plt.clf()

    for name, row in zip(names, results):
        print '%s\t%s' % (name, '\t'.join(map(str, row)))
        #print_matrix(results)







