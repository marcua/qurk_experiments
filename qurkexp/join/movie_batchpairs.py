#!/usr/bin/env python
import sys, os, math
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.join.movie_results import get_good_scenes
from qurkexp.hitlayer.models import HitLayer

from random import shuffle, seed

def get_params():
    if len(sys.argv) < 6:
        print 'not enough arguments!'
        print 'args: nscenes  batchsize  naive|smart  runname nassignments'
        exit()
    
    num_scenes = int(sys.argv[1])
    batch_size = int(sys.argv[2])

    if sys.argv[3] == "naive":
        smart = False
    elif sys.argv[3] == "smart":
        smart = True
    else:
        raise Exception("smart or naive interface?")

    run_name = sys.argv[4]

    nassignments = int(sys.argv[5])
    return (num_scenes, batch_size, smart, run_name, nassignments)



def ordered_pairs(num_scenes):
    pairs = []
    for i in get_actors():
        for j in get_scenes(num_scenes):
            pair = BPPair(left=i, right=j)
            pair.save()
            pairs.append(pair)
    return pairs

def get_actors():
    return range(1, 5+1)


_good_scenes = None
def get_scenes(num_scenes):
    global _good_scenes
    if not _good_scenes:
        _good_scenes = get_good_scenes('movie_nobatch_1')
    scenes = _good_scenes
    return scenes[:num_scenes]

def naive_batches(num_scenes, exp):
    pairs = ordered_pairs(num_scenes)
    nump = len(pairs)
    batch_size = exp.batch_size
    if exp.random:
        shuffle(pairs)
    pbatches = [pairs[i*batch_size: (i+1)*batch_size]
                for i in xrange(int(math.ceil(float(len(pairs)) / batch_size)))]
    batches = []

    for pbatch in pbatches:
        bpb = BPBatch(experiment=exp)
        bpb.save()
        map(lambda p: bpb.pairs.add(p), pbatch)
        bpb.save()
        batches.append(bpb)
    return batches

def smart_batches(num_scenes, exp):
    batches = []
    bsize = exp.batch_size
    left = get_actors()
    right = get_scenes(num_scenes)
    shuffle(left)
    shuffle(right)
    seed(0)

    lbatches = [left[i*bsize: (i+1)*bsize]
                for i in xrange(int(math.ceil(float(len(left)) / bsize)))]
    rbatches = [right[i*bsize: (i+1)*bsize]
                for i in xrange(int(math.ceil(float(len(right)) / bsize)))]

    for lbatch in lbatches:
        for rbatch in rbatches:
            bpb = BPBatch(experiment=exp)
            bpb.save()

            for x in lbatch:
                for y in rbatch:
                    pair = BPPair(left=x, right=y)
                    pair.save()
                    bpb.pairs.add(pair)

            bpb.save()
            batches.append(bpb)
    return batches

def post_batches(batches, smart, nassignments):
    desc = "Is the actor on the left the main focus of the scene on the right?"
    if smart:
        desc = "Click on pairs of images from the left and right columns, where the actor on the left is the main focus of the scene on the right."
    for b in batches:
        print 'batch',b.pk
        for p in b.pairs.all():
            print '\t',p.left, "\t", p.right

        hitid = HitLayer.get_instance().create_job("/celeb/movie/batchpairs/%d" % (b.id),
                                             ('celeb_batchpair', [b.id]),
                                             desc = desc,
                                             title = "Find actors in movie still images",
                                             price = 0.01,
                                             nassignments = nassignments)

if __name__ == "__main__":
    (num_scenes, batch_size, smart, run_name, nassignments) = get_params()
    exp = BPExperiment(run_name=run_name,
                       batch_size=batch_size,
                       smart_interface=smart,
                       random=True)
    exp.save()
    if smart:
        batches = smart_batches(num_scenes, exp)
    else:
        batches = naive_batches(num_scenes, exp)
    
    post_batches(batches, smart, nassignments)

#python movie_batchpairs.py 211 10 naive movie_all_naive_10_1 5
#python movie_batchpairs.py 211 5  naive movie_all_naive_5_1  5
#python movie_batchpairs.py 211 2  smart movie_all_smart_2_1  5
#python movie_batchpairs.py 211 3  smart movie_all_smart_3_1  5
#python movie_batchpairs.py 211 5  smart movie_all_smart_5_1  5

