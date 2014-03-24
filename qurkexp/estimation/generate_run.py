#!/usr/bin/env python
import random
import sys
import django_includes

from qurkexp.estimation.runs import load_run
from qurkexp.estimation.models import * 
from qurkexp.hitlayer.models import HitLayer

def initialize_run(run_name, dataset, estimate_vals, num_batches, batch_size, disp_style, assignments, price):
    ds = EstExp.objects.get(name=dataset)
    run = ExpRun.objects.create(name=run_name, exp=ds, num_batches=num_batches, batch_size=batch_size, display_style=disp_style, assignments=assignments, price=price)
    for val in estimate_vals:
        RunVal.objects.create(run=run, val=val)
    return run

def create_batches(run):
    items = list(ExpItem.objects.filter(exp__runs = run).distinct())
    for idx in range(run.num_batches):
        sample = random.sample(items, run.batch_size)
        batch = RunBatch.objects.create(run=run)
        batch.items_ptrs = sample
        batch.save()
        
def post_batches(run):
    title = "Identify various properties of images, text, or audio"
    desc = "You will be presented with several items (shapes, photos, videos, text, audio).  Below the items, you will see some questions regarding particular properties of those items (like color, or shape)."
    
    for b in run.batches.all():
        url = "/estimate/counts/%d/" % (b.id)
        hitid = HitLayer.get_instance().create_job(url,
                                             ('estimate_counts', [b.id]),
                                             desc = desc,
                                             title = title,
                                             price = run.price,
                                             nassignments = run.assignments)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("arguments: [run_name from run.py]")
    args = load_run(sys.argv[1])
    run = initialize_run(*args)
    create_batches(run)
    post_batches(run)
