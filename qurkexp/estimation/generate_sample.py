import django_includes
import random
import sys

from qurkexp.estimation.datasets import load_dataset, print_empirical_dist
from qurkexp.estimation.models import *

def index_props(kind, prop, dist):
    index = dict((v[0], []) for v in dist)
    items = Item.objects.filter(kind=kind)
    for item in items:
        a = item.annotations.get(prop=prop)
        index[a.val].append(item)
    return index

def generate_samples(exp, dist, num_samples):
    index = index_props(exp.kind, exp.prop, dist)
    for val, prob in dist:
        tosample = int(prob*num_samples)
        population = index[val]
        mult = tosample/len(population)
        mult += 0 if (tosample % len(population)) == 0 else 1
        samples = random.sample(population * mult, tosample)
        for samp in samples:
            ExpItem.objects.create(exp=exp, item=samp)

def sample(name, kind, prop, dist, num_samples):
    kind = Kind.objects.get(name=kind)
    exp = EstExp.objects.create(name=name, kind=kind, prop=prop)
    generate_samples(exp, dist, num_samples)
    print_empirical_dist(exp, dist)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("arguments: [dataset_name from datasets.py]")
    args = load_dataset(sys.argv[1])
    sample(*args)
