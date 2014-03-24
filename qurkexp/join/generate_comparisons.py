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
        print 'args: itemtype sorttype numitems batchsize sortsize nassignments runname'
        exit()
    
    item_type = sys.argv[1]
    sort_type = sys.argv[2]
    numitems = int(sys.argv[3])
    batch_size = int(sys.argv[4])
    sort_size = int(sys.argv[5])
    nassignments = int(sys.argv[6])
    run_name = sys.argv[7]
    
    if item_type not in ["squares", "animals"]:
        raise Exception("item type not matched")
    if sort_type not in ["cmp", "rating"]:
        raise Exception("sort type not matched")
    if sort_type == "rating" and sort_size != 1:
        raise Exception("Ratings can only have 1 item in each group")

    return (item_type, sort_type, numitems, batch_size, sort_size, nassignments, run_name)

def generate_vals(num_items, item_type):
    if item_type == "squares":
        vals = [CompVal(sortval=i, data=str(20+(3*i))) for i in range(1, num_items+1)]
        vals = []
        cur = 20
        idx = 1
        for i in range(1, 5):
            for j in range(10):
                vals.append(CompVal(sortval=idx, data=str(cur)))
                cur += i
                idx += 1
    elif item_type == "animals":
        vals = [CompVal(sortval=i, data=str(i)) for i in range(1, num_items+1)]
        
    else:
        raise Exception("I don't know how to make %s!" % (item_type))
    for val in vals:
        val.save()
    return vals

def generate_pairs(num_items, item_type):
    vals = generate_vals(num_items, item_type)
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

def comparison_batches(num_items, exp):
    pairs = generate_pairs(num_items, exp.item_type)
    batch = CompBatch(experiment=exp)
    while len(pairs) > 0:
        batch.save()
        (group, pairs) = generate_group(pairs, exp.sort_size, batch)
        if batch.compgroup_set.all().count() == exp.batch_size:
            batch = CompBatch(experiment=exp)

def rating_batches(num_items, exp):
    vals = generate_vals(num_items, item_type)
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
        DESC = {"squares":"Sort the squares by size.",
#                "animals":"Sort the animals by dangerousness."}
#                "animals":"Sort the animals by adult size."}
                "animals":"Sort the animals by how much they belong on saturn."}
    elif exp.sort_type == "rating":
        DESC = {"squares":"Rate the squares by size.",
#                "animals":"Rate the animals by dangerousness."}
#                "animals":"Rate the animals by adult size."}
                "animals":"Rate the animals by how much they belong on saturn."}

    for b in exp.compbatch_set.all():
        hitid = HitLayer.get_instance().create_job("/celeb/sort/%d" % (b.id),
                                             ('sort', [b.id]),
                                             desc = DESC[exp.item_type],
                                             title = DESC[exp.item_type],
                                             price = 0.01,
                                             nassignments = nassignments)

if __name__ == "__main__":
    (item_type, sort_type, numitems, batch_size, sort_size, nassignments, run_name) = get_params()
    exp = CompExperiment(run_name=run_name, batch_size=batch_size, sort_size=sort_size, sort_type=sort_type, item_type=item_type)
    exp.save()
    if sort_type == "cmp":
        comparison_batches(numitems, exp)
    elif sort_type == "rating":
        rating_batches(numitems, exp)
    post_batches(exp)
