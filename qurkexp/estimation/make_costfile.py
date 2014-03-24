from datasets import dataset_defs
from itertools import product

import os, sys
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.conf import settings

kind_vals = {}
for k, v in dataset_defs.items():
    kind_vals[v['kind']] = [item[0] for item in v['dist']]

for kind, vals in kind_vals.items():
    with open("%s/java/costfile_%s" % (settings.ROOT, kind), "w") as outf:
        for val1, val2 in product(vals, vals):
            outf.write("%s\t%s\t" % (val1, val2))
            if val1 == val2:
                outf.write("0\n")
            else:
                outf.write("1\n")
                
