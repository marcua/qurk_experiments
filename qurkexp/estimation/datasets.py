import django_includes

from qurkexp.estimation.models import *

dataset_defs = {
         'shape_blue_.1': { # also ..._test1, ..., 8
           'kind': 'shape',
           'prop': 'fill',
           'dist': [("red", .18), ("orange", .18), ("yellow", .18), ("green", .18), ("blue", .1), ("pink", .18)],
           'samples': 1000
         },
         'shape_yellowoutline_.1': { # also ..._test1, ..., 8
           'kind': 'shape',
           'prop': 'outline',
           'dist': [("yellow", .1), ("orange", .3), ("red", .3), ("green", .3), ("blue", 0.0), ("pink", 0.0)],
           'samples': 1000
         },
         'shape_triangle_.1': { # also ..._test1, ..., 8
           'kind': 'shape',
           'prop': 'shape',
           'dist': [("triangle", .1), ("circle", .3), ("square", .3), ("diamond", .3)],
           'samples': 1000
         },
         'shape_blue_.5': { 
           'kind': 'shape',
           'prop': 'fill',
           'dist': [("red", .1), ("orange", .1), ("yellow", .1), ("green", .1), ("blue", .5), ("pink", .1)],
           'samples': 1000
         },
         'gtav_male_.5': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .5), ("female", .5)],
           'samples': 1000
         },
         'gtav_male_.1': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .1), ("female", .9)],
           'samples': 1000
         },
         'gtav_male_.01': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .01), ("female", .99)],
           'samples': 1000
         },
         'gtav_male_.25': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .25), ("female", .75)],
           'samples': 1000
         },
         'gtav_male_.75': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .75), ("female", .25)],
           'samples': 1000
         },
         'gtav_male_.9': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .9), ("female", .1)],
           'samples': 1000
         },
         'gtav_male_.99': { 
           'kind': 'gtav',
           'prop': 'gender',
           'dist': [("male", .99), ("female", .01)],
           'samples': 1000
         },
         'wgat_normal': { 
           'kind': 'wgat',
           'prop': 'category',
           'dist': [("IS", .80), ("ME", .15), ("QF", .05)],
           'samples': 2500
         },
}

def load_dataset(run_name):
    if run_name not in dataset_defs:
        raise Exception("dataset_name not in experiment list (datasets.py)")
    ds = dataset_defs[run_name]
    return (run_name, ds['kind'], ds['prop'], ds['dist'], ds['samples'])

def get_empirical_dist(exp, dist):
    items = Item.objects.filter(exp_ptrs__exp = exp)
    counts = dict((v[0], 0.0) for v in dist)
    for item in items:
        a = item.annotations.get(prop=exp.prop)
        counts[a.val] += 1
    total = sum(count for val, count in counts.items())
    empirical = []
    for pair in dist:
        empirical.append((pair[0], counts[pair[0]]/total))
    return empirical

def print_empirical_dist(exp, dist):
    empirical = get_empirical_dist(exp, dist)
    print "theoretical distribution: %s" % (dist)
    print "empirical distribution: %s" % (empirical)
    return empirical

