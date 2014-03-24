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
            print "window: ", self.widx

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
        print mygold

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

if __name__ == '__main__':
    random.seed(0)

    # ratings = [[20, 1, 2, [], 0],
    #            [10, 1, 2, [], 1],
    #            [28, 1, 2, [], 2],
    #            [30, 1, 2, [], 3],
    #            [1, 1, 2, [], 4],
    #            [WINDOW0, 1, 2, [], WINDOW],
    #            [34, 1, 2, [], 6],
    #            [33, 1, 2, [], 7],
    #            [11, 1, 2, [], 8],
    #            [4, 1, 2, [], 9]]

    
    # # ratings = [[10-i, i, random.random(), [], i] for i in xrange(10)]
    # subset = [ratings[x] for x in [1, 4, WINDOW]]

    # reordered = reorder(ratings, subset)

    # for x in reordered:
    #     print x
    
    # exit()
    WINDOW = 5
    animalnames = map(lambda x: x.strip(), file('animalsort.txt', 'r').read().strip().split('\n'))

    if len(sys.argv) < 3:
        print 'hybrid.py gold_cmp_runname [list of runs]'
        exit()
    
    gold_name = sys.argv[1]
    run_names = sys.argv[2:]
    get_data = get_ratings
    allcmppairs = all_cmp_pairs([gold_name])
    #gold = get_gold(gold_name)
    #gold = dict([(int(k), v) for k,v in gold.items()])
    gold = None

    # for (k,v) in sorted(gold.items(), key=lambda x: x[1]):
    #     print '%s\t%d' % (animalnames[k-1], v)


    
    #ratings = get_data(run_names)
    # for d, m, s, a, i in ratings:
    #    print '%s\t%f\t%f\t%d\t%s' % (animalnames[d-1], m, s, i, ':'.join(map(str, a)))
    #get_tau(ratings)
    #exit()

    #stds = map(lambda x: x[2], get_data(run_names))
    #print numpy.mean(stds)
    #print numpy.std(stds)



    # for x in xrange(len(run_names)):
    #     ratings = get_data([run_names[x]])
    #     f = ConfidenceWindow(ratings).get_func()
    #     results.append(['confidence_%d' % x])
    #     for i in xrange(50):
    #         ratings = f(ratings)
    #         get_tau(ratings)
    

    options = [#('stdratings', std_ranges),
        ('randratings', random_ranges)
               #('maxstd', maxstd_ranges),
               #('pairs',farpairs_ranges),
               #('randbag', RandBag(get_data(run_names)).get_func())
        ]

    # for threshold in range(30, 61, 10):
    #     threshold /= 100.0
    #     ratings = get_data(run_names)
    #     f = PriorityWindow(ratings, threshold).get_func()
        #options.append(('priority_%d' % int(100*threshold), f))

    options.append(['confidence', ConfidenceWindow(get_data(run_names)).get_func()])

    #for i in [5,6]:
    #    options.append(('window%d' % (i), Window(i).make_window_ranges()))

    for name, f in options:
        ratings = get_data(run_names)

        results.append([name])
        get_tau(ratings)        
        #print name
        for i in xrange(100):
            ratings = f(ratings)
            get_tau(ratings)
            #for d, m, s, a, i in ratings:
            #    print '%d\t%f\t%f\t%d\t%s' % (d, m, s, i, ':'.join(map(str, a)))


    print_matrix(results)

