#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.join.movie_results import get_actor_scenes
from qurkexp.hitlayer.models import HitLayer

from random import shuffle, seed

def get_params():
    if len(sys.argv) < 7:
        print 'not enough arguments!'
        print 'args: [cmp|rating] join_exp_name actorid batchsize sortsize nassignments runname'
        exit()
    
    sort_type = sys.argv[1]
    join_exp = sys.argv[2]
    actorid = int(sys.argv[3])
    batch_size = int(sys.argv[4])
    sort_size = int(sys.argv[5])
    nassignments = int(sys.argv[6])
    run_name = sys.argv[7]

    sceneids = get_actor_scenes(actorid, join_exp)
    sceneids = map(lambda x: x[0],sceneids)
    
    if sort_type not in ["cmp", "rating"]:
        raise Exception("sort type not matched")
    if sort_type == "rating" and sort_size != 1:
        raise Exception("Ratings can only have 1 item in each group")

    return (sort_type, actorid, sceneids, batch_size, sort_size, nassignments, run_name)


def generate_vals(sceneids):
    vals = [CompVal(sortval=i, data=sceneid) for i, sceneid in enumerate(sceneids)]
    map(lambda x: x.save(), vals)
    return vals

def generate_pairs(sceneids):
    vals = generate_vals(sceneids)
    seed(1)
    shuffle(vals)
    pairs = []
    for i,l in enumerate(vals[:len(vals)-1]):
        for r in vals[i+1:]:
            pairs.append((l,r))
    return pairs

    

def generate_group(pairs, sort_size, batch):
    groupvals = set()
    rempairs = []
    for pair in pairs:
        sp = set(pair)
        if len(groupvals | sp) <= sort_size:
            groupvals |= sp
            rempairs.append(pair)
        else:
            break
    for pair in rempairs:
        pairs.remove(pair)
    group = CompGroup(batch=batch)
    group.save()
    
    for val in groupvals:
        group.vals.add(val)
    return (group, pairs)

def comparison_batches(sceneids, exp):
    pairs = generate_pairs(sceneids)
    batch = CompBatch(experiment=exp)
    while len(pairs) > 0:
        batch.save()
        (group, pairs) = generate_group(pairs, exp.sort_size, batch)
        if batch.compgroup_set.all().count() == exp.batch_size:
            batch = CompBatch(experiment=exp)

def rating_batches(sceneids, exp):
    vals = generate_vals(sceneids)
    seed(1)
    shuffle(vals)
    batch = CompBatch(experiment=exp)
    for val in vals:
        batch.save()
        group = CompGroup(batch=batch)
        group.save()
        group.vals.add(val)
        if batch.compgroup_set.all().count() == exp.batch_size:
            batch = CompBatch(experiment=exp)


def post_batches(exp):
    if exp.sort_type == "cmp":
        desc = "Sort how flattering movie scenes are"
    elif exp.sort_type == "rating":
        desc = "Rate how flattering movie scenes are"

    for b in exp.compbatch_set.all():
        hitid = HitLayer.get_instance().create_job("/celeb/movie/sort/%d" % (b.id),
                                             ('sort', [b.id]),
                                             desc = desc,
                                             title = desc,
                                             price = 0.01,
                                             nassignments = nassignments)

if __name__ == "__main__":
    (sort_type, actorid, sceneids, batch_size, sort_size, nassignments, run_name) = get_params()
    exp = CompExperiment(run_name=run_name, batch_size=batch_size,
                         sort_size=sort_size, sort_type=sort_type,
                         item_type='movie_%d' % actorid)
    exp.save()

    if sort_type == "cmp":
        comparison_batches(sceneids, exp)
    elif sort_type == "rating":
        rating_batches(sceneids, exp)


    post_batches(exp)

# movie_all_naive_10_1 
# movie_all_naive_5_1  
# movie_all_smart_2_1  
# movie_all_smart_3_1  
# movie_all_smart_5_1  

#for actorid in range(1,5+1):
# "python movie_comparisons.py cmp    movie_all_naive_5_1 %d 5 5 5 movie_cmp_%d_5_5_5" % actorid
# "python movie_comparisons.py rating movie_all_naive_5_1 %d 5 1 5 movie_rat_%d_5_1_5" % actorid

