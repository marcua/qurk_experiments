import csv
import sys,os
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/error_summary.pdf')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from collections import defaultdict
from django.conf import settings
from qurkexp.estimation.models import *
from qurkexp.hitlayer.models import *
from qurkexp.estimation.runs import run_defs

import pytz

def pretty_names(names):
    interface = {
        'tile': 'C',
        'batch': 'L'
    }
    pnames = []
    for name in names:
        run = run_defs[name]
        pretty = "%s%d" % (interface[run['display_style']], run['batch_size'])
        pnames.append(pretty)

    return pnames

PRETTY_NAMES = {
    'simpleavg_0_absolute': 'Avg',
    'weightedavg_0.86_absolute': 'Thresh',
    'batch_novar_absolute': 'LabelR',
    'noredundant_novar_absolute': 'LabelNoR'
}

def plot_techniques(techs):
#    names = pretty_names([l[0] for l in latencies])
    names = [k for k in techs.keys()]
    meds = [techs[k]['avg'] for k in names]
    mini = [p[1]-techs[p[0]]['min'] for p in zip(names, meds)]
    maxi = [techs[p[0]]['max']-p[1] for p in zip(names, meds)]
    names = [PRETTY_NAMES[name] for name in names]
    ind = np.arange(len(names))    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
    
    p1 = plt.bar(ind, meds, width, color='y', yerr=[mini, maxi])
    
    plt.ylabel('Error range')
    plt.xlabel('Techniques')
#    plt.title('Error ranges of various techniques on GTAV')
    plt.xticks(ind+width/2., names)
#    plt.yticks(np.arange(0,81,10))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def read_csv(input_csv):
    reader = csv.DictReader(open(input_csv, 'rU'), dialect='excel')
    techniques = defaultdict(dict)
    for r in reader:
        for k,v in r.items():
            if k != "measure":
                techniques[k][r['measure']] = float(v)
    return techniques

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'arguments: input_csv'
        exit()

    input_csv = sys.argv[1]
    techs = read_csv(input_csv)
    plot_techniques(techs)
    pp.close()
