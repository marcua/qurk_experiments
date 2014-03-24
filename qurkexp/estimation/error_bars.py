import csv
import sys,os
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/error_bars.pdf')
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
matplotlib.rcParams['lines.linewidth'] = 2

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

def autolabel(rects, labels, sub):
    # attach some text labels
    for rect, label in zip(rects, labels):
        sub.text(rect.get_x()+rect.get_width()/2., rect.get_height()+.005, label, fontsize=11, ha='center', va='bottom')

TICKS = ['LabelNoR', 'LabelR', 'Thresh', 'Avg']
#COLORS = ['w', 'y', 'c', 'm']
COLORS = ['w', '#D1D3D4', '#9D9FA2', '#6D6E71']
def plot_batch(bybatch, width, bar_offsets, label_offsets, grouping):
    sub = plt.figure().add_subplot(111)
    plt.subplots_adjust(right=.99)
    plt.subplots_adjust(left=.1)
    for idx, tech in enumerate(TICKS):
        batches = []
        sizes = bybatch[tech]
        for size in sorted(sizes.keys()):
            vals = sizes[size]
            if size < 1.0:
                size = str(size).lstrip("0")
            else:
                size = str(size)
            batches.append((size, (min(vals), max(vals), sum(vals)/len(vals))))
        ind = [bar_offsets[idx]+(width*x) for x in range(len(batches))]
        minis = [p[1][2]-p[1][0] for p in batches]
        maxis = [p[1][1]-p[1][2] for p in batches]
        avgs = [p[1][2] for p in batches]
        p1 = sub.bar(ind, avgs, width, color=COLORS[idx], ecolor='c', yerr=[minis, maxis])
        autolabel(p1, [p[0] for p in batches], sub)
    sub.set_ylabel('Error range')
    sub.set_xlabel('Techniques (by %s)' % grouping)
#    plt.title('Error ranges of various techniques on GTAV')
    sub.set_xticks(label_offsets)
    sub.set_xticklabels(TICKS)
    
#    plt.yticks(np.arange(0,81,10))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

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
    bybatch = defaultdict(lambda: defaultdict(list))
    byselect = defaultdict(lambda: defaultdict(list))
    for r in reader:
        parts = r['run'].split("_")
        if parts[-2] != "male":
            continue
        batch = int(filter(lambda x: x.startswith("size"), parts)[0].lstrip("size"))
        select = float(parts[2])
        if "batch" in r['run']:
            if "noredundancy" in r['run']:
                tech = "LabelNoR"
            else:
                tech = "LabelR"
            bybatch[tech][batch].append(float(r['batch_novar_absolute']))
            byselect[tech][select].append(float(r['batch_novar_absolute']))
        else:
            bybatch['Avg'][batch].append(float(r['simpleavg_0_absolute']))
            byselect['Avg'][select].append(float(r['simpleavg_0_absolute']))
            bybatch['Thresh'][batch].append(float(r['weightedavg_0.86_absolute']))
            byselect['Thresh'][select].append(float(r['weightedavg_0.86_absolute']))
    return byselect, bybatch

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'arguments: input_csv'
        exit()

    input_csv = sys.argv[1]
    byselect, bybatch = read_csv(input_csv)
    plot_batch(bybatch, .16, [.1, .9, 1.68, 3.09], [.4, 1.2, 2.33, 3.71], "batch size")
    plot_batch(byselect, .15, [.01, 1.15, 2.28, 3.4], [.53, 1.65, 2.79, 3.91], "selectivity of males")
#    plot_select(byselect)
#    plot_techniques(techs)
    pp.close()
