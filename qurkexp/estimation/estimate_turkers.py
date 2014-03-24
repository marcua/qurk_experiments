import sys,os,base64,time,traceback
import django_includes
import numpy as np
import time
import random
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/test.pdf')
import matplotlib.pyplot as plt

from collections import defaultdict
from datetime import datetime
from qurkexp.estimation.models import *
from qurkexp.estimation.datasets import load_dataset, get_empirical_dist
from qurkexp.estimation.runs import load_run

def update_data(users, run, prop, val, actual):
    vras = ValRespAns.objects.filter(vrm__batch__run = run).filter(val=val).select_related()
    idx = 0
    for vra in vras:
        idx += 1
#        user = users.get(vra.vrm.wid, [])
#        users[vra.vrm.wid] = user
        ptrs = vra.vrm.batch.items_ptrs
        total = 1.0*ptrs.count()
        estf = vra.count/total
        sc = Annotation.objects.filter(item__exp_ptrs__batches = vra.vrm.batch).filter(prop=prop).filter(val=val).count()
        sampf = sc/total
        seconds = vra.vrm.seconds_spent
        height = vra.vrm.screen_height
        width = vra.vrm.screen_width
        users[vra.vrm.wid].append({'estf': estf, 'sampf': sampf, 'actual': actual, 'seconds': seconds, 'height': height, 'width': width})
    print "idx", idx

def print_users(run_name, users):
    srt = sorted(users.items(), key=lambda x: len(x[1]), reverse=True)
    print "run_name", "user", "num_questions", "avg_seconds", "avg_screen_height", "avg_screen_width", "samperr", "acterr"
    for user, answers in srt:
        num = len(answers)
        samperr = np.average([abs(ans['estf']-ans['sampf']) for ans in answers])
        acterr = np.average([abs(ans['estf']-ans['actual']) for ans in answers])
        seconds = np.average([ans['seconds'] for ans in answers])
        height = np.average([ans['height'] for ans in answers])
        width = np.average([ans['width'] for ans in answers])
        print run_name, user, num, seconds, height, width, samperr, acterr

def estimate(run_name):
    run = ExpRun.objects.get(name=run_name)
    runvals = RunVal.objects.filter(run=run)
    exp = run.exp
    prop = exp.prop
    actual = load_dataset(exp.name)[3]
    empirical = get_empirical_dist(exp, actual)

    users = defaultdict(list)
    for val in runvals:
        update_data(users, run, prop, val.val, dict(empirical)[val.val])
    print_users(run_name, users)
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("arguments: run_name")
    for run_name in sys.argv[1:]:
        estimate(run_name)
