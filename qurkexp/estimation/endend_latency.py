import sys,os
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/endend_latencies.pdf')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.conf import settings
from qurkexp.estimation.models import *
from qurkexp.hitlayer.models import *
from qurkexp.estimation.runs import run_defs

import pytz

def tot_time(start, end):
    delta = timedelta(hours=5, minutes=0) # we ran a hit and finished it fast, and this was the delta.
# This was the delta from our sort/joins paper
#    delta = timedelta(hours=4, minutes=53) # we ran a hit and finished it fast, and this was the delta.
    totaltime = end-start-delta
    totaltime = (totaltime.days*24*3600.0 + totaltime.seconds)/3600.0
    return totaltime

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

def get_latency(expname):
    resps = ValRespMeta.objects.filter(batch__run__name = expname)
    hitids = set(resp.hid for resp in resps)
    hits = HIT.objects.filter(hid__in = hitids)
    start = min(hit.start_tstamp for hit in hits)
    endtimes = [resp.submit_time for resp in resps]
    end_max = max(endtimes)
    tot_max = tot_time(start, end_max)
    end_95ptile = sorted(endtimes)[int(len(endtimes)*.95)]
    tot_95ptile = tot_time(start, end_95ptile)
    end_50ptile = sorted(endtimes)[int(len(endtimes)*.50)]
    tot_50ptile = tot_time(start, end_50ptile)
    retval = (expname, tot_max, tot_95ptile, tot_50ptile)
    print "%s, %f, %f, %f" % retval
    return retval

def plot_latencies(latencies):
    names = pretty_names([l[0] for l in latencies])
    tot_95 = [l[2] for l in latencies]
    tot = [l[1]-l[2] for l in latencies]
    ind = np.arange(len(latencies))    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
    
    p1 = plt.bar(ind, tot_95, width, color='r')
    p2 = plt.bar(ind, tot, width, color='y', bottom=tot_95)
    
    plt.ylabel('Completion time for 1000 HITs (hours)')
    plt.xlabel('Experiment')
    plt.title('Completion times per experiment (1000 HITs)')
    plt.xticks(ind+width/2., names )
#    plt.yticks(np.arange(0,81,10))
    plt.legend( (p1[0], p2[0]), ('95th Percentile', '100th Percentile') )
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'arguments: [run names]'
        exit()

    expnames = sys.argv[1:]
    print "expname, tot_max, tot_95ptile, tot_50ptile"
    latencies = [get_latency(expname) for expname in expnames]
    plot_latencies(latencies)
    pp.close()
