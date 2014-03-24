import sys,os,base64,time,traceback
import django_includes
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/interface-latencies.pdf')
import matplotlib.pyplot as plt
from qurkexp.estimation.models import *
from qurkexp.estimation.runs import run_defs
import matplotlib.pyplot as plt

def get_latency(run_name):
    vrms = ValRespMeta.objects.filter(batch__run__name = run_name)
    return [vrm.seconds_spent for vrm in vrms]

def plot_latencies(names, latencies):
    fig = plt.figure()
    sub = fig.add_subplot(111)
    sub.boxplot(latencies, whis=30)
    sub.set_ylim((0,80))
    sub.set_xticklabels(names, size="small")
#    sub.set_title("Distribution of seconds to complete HITs")
    plt.ylabel('HIT completion time (seconds) of various experiments')
#    plt.xlabel('Experiment')
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def pretty_names(names):
    ds = {
        'gtav': 'Face',
        'shape_trian': 'Shape',
        'shape_yellow': 'Color',
        'wgat': 'Tweet',
    }
    interface = {
        'tile': 'C',
        'batch': 'L'
    }
    pnames = []
    for name in names:
        dataset = None
        for k, v in ds.items():
            if name.startswith(k):
                dataset = v
        run = run_defs[name]
        ammt = ""
        if 'male' in name:
            ammt = "0%s" % name.split("_")[2]
        pretty = "%s%d\n%s\n%s" % (interface[run['display_style']], run['batch_size'], dataset, ammt)
        pnames.append(pretty)

    return pnames

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("arguments: run_names")
    latencies = []
    for run_name in sys.argv[1:]:
        latencies.append(get_latency(run_name))
    pnames = pretty_names(sys.argv[1:])
    plot_latencies(pnames, latencies)
    pp.close()
