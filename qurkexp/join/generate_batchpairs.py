#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import * 
from qurkexp.hitlayer.models import HitLayer

from random import shuffle, seed

def get_params():
    if len(sys.argv) < 7:
        print 'not enough arguments!'
        print 'args: ncelebs  batchsize  naive|smart  random|ordered  runname nassignments'
        exit()
    
    num_celebs = int(sys.argv[1])
    batch_size = int(sys.argv[2])
    if sys.argv[3] == "naive":
        smart = False
    elif sys.argv[3] == "smart":
        smart = True
    else:
        raise Exception("smart or naive interface?")
    if sys.argv[4] == "random":
        random = True
    elif sys.argv[4] == "ordered":
        random = False
    else:
        raise Exception("random or ordered pairs?")

    run_name = sys.argv[5]

    nassignments = int(sys.argv[6])
    return (num_celebs, batch_size, smart, random, run_name, nassignments)

def ordered_pairs(num_celebs):
    pairs = []
    for i in range(1, num_celebs+1):
        for j in range(1, num_celebs+1):
            pair = BPPair(left=i, right=j)
            pair.save()
            pairs.append(pair)
    return pairs

def naive_batches(num_celebs, exp):
    pairs = ordered_pairs(num_celebs)
    nump = len(pairs)
    batch_size = exp.batch_size
    if exp.random:
        shuffle(pairs)
    batches = []
    for i in range(0, nump, batch_size):
        bpb = BPBatch(experiment=exp)
        bpb.save()
        for p in pairs[i:min(i+batch_size, nump)]:
            bpb.pairs.add(p)
        bpb.save()
        batches.append(bpb)
    return batches

def smart_batches(num_celebs, exp):
    batches = []
    left = range(1,num_celebs+1)
    right = range(1,num_celebs+1)
    shuffle(left)
    shuffle(right)
    seed(0)
    for i in range(0, num_celebs, exp.batch_size):
        for j in range(0, num_celebs, exp.batch_size):
            bpb = BPBatch(experiment=exp)
            bpb.save()
            for x in range(i, min(i+exp.batch_size, num_celebs)):
                for y in range(j, min(j+exp.batch_size, num_celebs)):
                    pair = BPPair(left=left[x], right=right[y])
                    pair.save()
                    bpb.pairs.add(pair)
            bpb.save()
            batches.append(bpb)
    return batches

def post_batches(batches, smart, nassignments):
    desc = "Decide if the celebrity on the left is the same as the one on the right"
    if smart:
        desc = "Drag the picture of the celebrity on the left to the matching one of the celebrity on the right"
    for b in batches:
        hitid = HitLayer.get_instance().create_job("/celeb/batchpairs/%d" % (b.id),
                                             ('celeb_batchpair', [b.id]),
                                             desc = desc,
                                             title = "Compare celebrity pictures",
                                             price = 0.01,
                                             nassignments = nassignments)

if __name__ == "__main__":
    (num_celebs, batch_size, smart, random, run_name, nassignments) = get_params()
    exp = BPExperiment(run_name=run_name, batch_size=batch_size, smart_interface=smart, random=random)
    exp.save()
    if smart:
        batches = smart_batches(num_celebs, exp)
    else:
        batches = naive_batches(num_celebs, exp)
    
    post_batches(batches, smart, nassignments)
