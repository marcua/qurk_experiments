import sys,os,base64,time,traceback
import django_includes
import numpy as np
import time
import random
import json
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = None
import matplotlib.pyplot as plt
matplotlib.rcParams['lines.linewidth'] = 2

from collections import defaultdict, Counter
from csv import DictWriter
from datetime import datetime
from math import log, exp, isnan, sqrt
from qurkexp.estimation.models import *
from qurkexp.estimation.datasets import load_dataset, get_empirical_dist
from qurkexp.estimation.runs import load_run
from qurkexp.join.gal import run_gal
from scipy.optimize import fmin, fmin_bfgs, fmin_cobyla, fmin_l_bfgs_b
from scipy.cluster.vq import vq, kmeans, whiten

TECH_COMBOS = {
    'sawam': [('simpleavg', [0]),
#              ('median', [0]),
#              ('kmeans', [0]),
#              ('middle_avg', [0.05, 0.1, 0.5]),
              ('weightedavg', [.86]),#[.75, .80, .85, .90, .95]),
              ('min', [1.1])],#[.10, .20, .30, .40, .50, .60, .70, .80, .90, 1, 1.1, 1.2, 1.3, 1.4, 1.5])]
    'wa': [('weightedavg', [.86])],
    'm': [('min', [1.1])],
    'sam': [('simpleavg', [0]),
              ('min', [1.1])],#[.10, .20, .30, .40, .50, .60, .70, .80, .90, 1, 1.1, 1.2, 1.3, 1.4, 1.5])]
    'sawa': [('simpleavg', [0]),
              ('weightedavg', [.86])],#[.10, .20, .30, .40, .50, .60, .70, .80, .90, 1, 1.1, 1.2, 1.3, 1.4, 1.5])]
    'sawam_crazy': [('simpleavg', [0]),
#              ('median', [0]),
#              ('kmeans', [0]),
#              ('middle_avg', [0.05, 0.1, 0.5]),
              ('weightedavg', [.8, .81, .82, .83, .84, .85, .86, .87, .88, .89, .9]),#[.75, .80, .85, .90, .95]),
              ('min', [1.1])],#[.10, .20, .30, .40, .50, .60, .70, .80, .90, 1, 1.1, 1.2, 1.3, 1.4, 1.5])]
    
}
TECHNIQUES = None
SAMPLE_LEADING = True
DUMMY_CALC = False
#NUM_SAMPLES = 50
NUM_SAMPLES = 100
SAMPLE_INTERVAL = 5 # measure error rate in samples that are multiples of this number
WA_ITERATIONS = 10
USER_LIMIT = 1
KEYS = ['estf']#, 'sampf']

FRACS_CACHE = {}
VALS_CACHE = {}

def score_dict(fracs):
    retval = {}
    for key in KEYS:
        retval[key] = np.average([frac[key] for frac in fracs])
    return retval

def median(fracs):
    retval = {}
    for key in KEYS:
        retval[key] = np.median([frac[key] for frac in fracs])
    return retval

def middle_avg(fracs, width):
    retval = {}
    for key in KEYS:
        sort = sorted(frac[key] for frac in fracs)
        mid = len(fracs)/2.0
        width = (width*len(fracs))/2.0
        retval[key] = np.average(sort[int(mid-width):int(mid+width)])
    return retval


def kmeans_est(fracs):
    uservals = defaultdict(list)
    for frac in fracs:
        uservals[frac['user']].append(frac['estf'])
    features, ids = [], []
    for user, vals in uservals.items():
        features.append([np.mean(vals)])
        ids.append(user)

    features = whiten(np.array(features))
    centroids = kmeans(features, 5)[0]
    groups = vq(features, centroids)[0]

    largest = Counter(groups).most_common(1)[0][0]
    uweights = defaultdict(lambda: 1.0)
    for user, group in zip(ids, groups):
        if group != largest:
            uweights[user] = 0.0
    
    vals, weights = zip(*[(frac['estf'], uweights[frac['user']]) for frac in fracs])
    retval = {'estf': np.average(vals, weights=weights)}
    return retval


def get_samples(fracs, actually_sample):
    new_fracs = fracs
    if actually_sample:
        counts = defaultdict(lambda: 0)
        shuffled = random.sample(fracs, len(fracs))
        new_fracs = []
        for shuffle in shuffled:
            if counts[shuffle['user']] < USER_LIMIT:
                new_fracs.append(shuffle)
                counts[shuffle['user']] += 1
    return new_fracs

def get_averages(fracs, key, actually_sample):
    new_fracs = fracs
    if actually_sample:
        user_vals = defaultdict(list)
        for frac in fracs:
            user_vals[frac['user']].append(frac)
        new_fracs = []
        for uv in user_vals.values():
            new_frac = dict(uv[0])
            new_frac[key] = np.average([f[key] for f in uv])
            new_frac[key+"_std"] = np.std([f[key] for f in uv])
            new_fracs.append(new_frac)
    return new_fracs

# Weigh each worker's contribution to the average by their bias from the average.
def weight_adjust(fracs, threshold):
    retval = {}
    for key in KEYS:
        uweights = defaultdict(lambda: 1.0)
        user_avgs = get_averages(fracs, key, True)
        for idx in xrange(WA_ITERATIONS):
            new_fracs = user_avgs if idx<(WA_ITERATIONS-1) else fracs
#            new_fracs = get_averages(fracs, key, idx<(WA_ITERATIONS-1))#get_samples(fracs, idx<(WA_ITERATIONS-1))
            vals = [frac[key] for frac in new_fracs]
            weights = [uweights[frac['user']] for frac in new_fracs]
            if sum(weights) == 0:
                retval[key] = np.average(vals)
                break
            else:
                retval[key] = np.average(vals, weights=weights)
            uweights = defaultdict(list)
            for frac in fracs:
                diff = 1-abs(frac[key]-retval[key])
                uweights[frac['user']].append(diff)
            uweights = dict((u, np.average(w) if np.average(w) > threshold else 0) for u, w in uweights.items())
    return retval

# Weigh each person by the weight that minimizes the total overall distance to the average.
def weight_optimize(fracs, lamb):
    retval = {}
    for key in KEYS:
        uweights = defaultdict(lambda: 1.0)
        user_avgs = get_averages(fracs, key, True)
        for idx in xrange(WA_ITERATIONS):
            new_fracs = user_avgs if idx<(WA_ITERATIONS-1) else fracs
            vals = [frac[key] for frac in new_fracs]
            weights = [uweights[frac['user']] for frac in new_fracs]
            if sum(weights) == 0:
                retval[key] = np.average(vals)
                retval[key+"_weights"] = defaultdict(lambda: 1.0)
                break
            else:
                retval[key] = np.average(vals, weights=weights)

            if idx < (WA_ITERATIONS - 1):
                uweights = opt_weights(retval[key], user_avgs, key, uweights, lamb)
                retval[key+"_avgs"] = new_fracs
            else:
                retval[key+"_weights"] = uweights
    return retval

def opt_weights(approx_avg, user_avgs, key, oldweights, lamb):
    users, diffs = [], []
    for user in user_avgs:
        users.append(user['user'])
        diff = approx_avg - user[key]
        diffs.append(abs(diff))
    """
    def func(weights):
        udiff = sum(weight*diff for weight, diff in zip(weights, diffs))
        retval = udiff/(1.0*sum(diffs)) + lamb*(len(weights) - sum(weights))/(1.0*len(weights))
        return abs(retval)

    bounds = [(0.0,1.0)]*len(oldweights)
    optweights = fmin_l_bfgs_b(func, weight_guess, bounds=bounds, approx_grad=True, disp=False)[0]
    """
    limit = (1.0*lamb)/len(users)
    denom = sum(diffs)
    if denom > 0:
        optweights = [0.0 if diff/denom > limit else 1.0 for diff in diffs]
    else:
        optweights = [1]*len(users)

    #print "ow, avgs", zip(optweights, [np.mean(uf) for uf in user_fracs]), approx_avg
    return dict(zip(users, optweights))

def maybe_update_avgstd(stats, samples, numhits):
    retval = {}
    for key in KEYS:
        if len(samples) > 0:
            keys = [samp[key] for samp in samples]
            keys.sort()
            stats.append({
                    key+"_avg": np.average(keys),
                    key+"_std": np.std(keys),
                    key+"_.025": keys[int(len(keys)*.025)],
                    key+"_.975": keys[int(len(keys)*.975)],
                    key+"_allkeys": keys,
                    "numhits": numhits
                    })

def sample_frac_stats(fracs, tech, var, sample_leading):
    """
    Given a set of fractions from user responses, calculates the avg and stdev of
      estimates of technique 'tech' on multiple samples of different size
      samples of the fractions.
    returns [stats0, ..., statsN]
       Where statsI contains the average and standard deviation of NUM_SAMPLES
          samples of I items from the worker responses.
        The format of sampleI is {'estf_avg': AVG, 'estf_std': STD}
    """
#    sys.stderr.write("technique, %s, %f\n" % (tech, var))
    all_samples = []
    for idx in xrange(len(fracs)+1):
        all_samples.append([])
    for idx in xrange(NUM_SAMPLES):
        shuffled = random.sample(fracs, len(fracs))
        lower_limit = 1 if sample_leading else len(fracs)
        for idx2 in xrange(lower_limit, len(fracs)+1):
            if sample_leading and ((idx2 % SAMPLE_INTERVAL) != 0):
                continue
            if tech == "simpleavg":
                all_samples[idx2].append(score_dict(shuffled[:idx2]))
            elif tech == "median":
                all_samples[idx2].append(median(shuffled[:idx2]))
            elif tech == "kmeans":
                all_samples[idx2].append(kmeans_est(shuffled[:idx2]))
            elif tech == "middle_avg":
                all_samples[idx2].append(middle_avg(shuffled[:idx2], var))
            elif tech == "weightedavg":
                all_samples[idx2].append(weight_adjust(shuffled[:idx2], var))
            elif tech == "min":
                all_samples[idx2].append(weight_optimize(shuffled[:idx2], var))
            else:
                raise Error("unknown estimation type")
    stats = []
    for idx, samps in enumerate(all_samples):
        maybe_update_avgstd(stats, samps, idx+1)
#    print "final", stats[-1]
    # plot spammers and good turkers as decided on by the minimization algorithm
#    if tech == "min":
#        plot_users(all_samples[-1][-1], np.mean([frac['sampf'] for frac in fracs]))
    return stats

def sample_value_stats(values, val, batch_size, sample_leading):
    """
    Given a list of batched item labels from user responses,
      calculates the avg and stdev of fraction of items with property
      'val' on multiple samples of different size samples of the items

    values is a dict with items of the form
      batchid->{'numresp': nnn, 'items': [{'item': expitem_pk, 'galval': yyy, 'actval': yyx}]*}

    returns [stats0,
      ..., statsN] Where statsI contains the average and standard
      deviation of NUM_SAMPLES samples of I items from the worker
      responses.  The format of sampleI is {'estf_avg': AVG,
      'estf_std': STD}
    """
    all_samples = []
    totalresp = sum(v['numresp'] for v in values.values())
    for idx in xrange(totalresp+1):
        all_samples.append([])
    for idx in xrange(NUM_SAMPLES):
        shuffled = random.sample(values.values(), len(values))
        numresp, acthave, galhave, total = 0, 0.0, 0.0, 0.0
        for batch in shuffled:
            numresp += batch['numresp']
            if sample_leading or (numresp == totalresp):
                for item in batch['items']:
                    galhave += 1 if item['galval'] == val else 0
                    acthave += 1 if item['actval'] == val else 0
                    total += 1
                if (numresp % SAMPLE_INTERVAL) == 0:
                    all_samples[numresp].append({'estf': galhave/total, 'sampf': acthave/total})
    stats = []
    for idx, samps in enumerate(all_samples):
        maybe_update_avgstd(stats, samps, idx)
    return stats
            
def plot_users(userdata, actual):
    # plot users by classification
    sub = plt.figure().add_subplot(111)
    sub.errorbar([-1, 2], [actual, actual], fmt="r-")
    xs, ys, err = [], [], []
    for userdict in userdata['estf_avgs']:
        xs.append(userdata['estf_weights'][userdict['user']])
        ys.append(userdict['estf'])
        err.append(userdict['estf_std'])
    sub.errorbar(xs, ys, xerr=err, fmt="x")
    sub.set_ylim((0,1))
    sub.set_xlim((-1, 2))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

    # plot users by distance to avg and variance
    sub = plt.figure().add_subplot(111)
    xs, ys, err = [], [], []
    good = {'xs': [], 'ys':[]}
    spammer = {'xs': [], 'ys':[]}
    for userdict in userdata['estf_avgs']:
        if userdata['estf_weights'][userdict['user']] > .99:
            plot_group = good
        else:
            plot_group = spammer
        plot_group['xs'].append(abs(userdict['estf'] - actual))
        plot_group['ys'].append(userdict['estf_std'])
    sub.scatter(good['xs'], good['ys'], color="b", label="good")
    sub.scatter(spammer['xs'], spammer['ys'], color="r", label="spammer")
    sub.set_ylim((0,1))
    sub.set_xlim((0, 1))
    sub.legend()
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()
    
def get_fracs(prop, val, run):
    cachename = "%s_%s_%s" % (run.name, prop, val)
    fracs = FRACS_CACHE.get(cachename, None)
    if fracs == None:
        vras = ValRespAns.objects.filter(vrm__batch__run = run).filter(val=val).select_related()
        fracs = []
        for vra in vras:
            ptrs = vra.vrm.batch.items_ptrs
            total = 1.0*ptrs.count()
            estf = vra.count/total
            sc = Annotation.objects.filter(item__exp_ptrs__batches = vra.vrm.batch).filter(prop=prop).filter(val=val).count()
            sampf = sc/total
            fracs.append({'estf': estf, 'sampf': sampf, 'user': vra.vrm.wid, 'total': total})
        FRACS_CACHE[cachename] = fracs
    return fracs

def get_values(prop, run):
    """
    calls get another label on all the values emitted by a run on a property
    returns: dict of batchid->{'numresp': nnn, 'items': [{'item': expitem_pk, 'galval': yyy, 'actval': yyx}]*}
    """
    cachename = "%s_%s" % (run.name, prop)
    batchresps = VALS_CACHE.get(cachename, None)
    if batchresps == None:
        vrvs = ValRespValue.objects.filter(vrm__batch__run = run)
        batchresps = defaultdict(set)
        data = []
        num_responses = 0
        for vrv in vrvs:
            data.append(["%d_%d" % (vrv.vrm.batch.pk, vrv.item.pk), vrv.vrm.wid, vrv.val])
            batchresps[vrv.vrm.batch.pk].add(vrv.vrm.wid)
            num_responses = len(batchresps[vrv.vrm.batch.pk])
        values = defaultdict(list)
        if num_responses > 1: # run get-another-label
            spammers, results = run_gal(run.exp.kind.name, data)
            for k, v in results:
                batch, item = map(int, k.split("_"))
                maxprob = max(r[1] for r in v)
                maxval = filter(lambda x: x[1] == maxprob, v)[0][0]
                actval = Annotation.objects.get(item__exp_ptrs__pk = item, prop = prop).val
                values[batch].append({'item': str(item), 'galval': maxval, 'actval': actval})
        else: # we have no redundancy, so can't run GAL
            for k, wid, val in data:
                batch, item = map(int, k.split("_"))
                actval = Annotation.objects.get(item__exp_ptrs__pk = item, prop = prop).val
                values[batch].append({'item': str(item), 'galval': val, 'actval': actval})
        for batch, items in values.items():
            batchresps[batch] = {'numresp': len(batchresps[batch]), 'items': items}
        VALS_CACHE[cachename] = batchresps
    return batchresps

def get_fracs_dummy():
    with open("fracs.json") as f:
        return json.loads("".join(f.readlines()))

def write_fracs_dummy(fracs):
    with open("fracs.json", "w") as f:
        f.write(json.dumps(fracs))

def estimate_val_values(prop, val, run):
    values = get_values(prop, run)
    return sample_value_stats(values, val, run.batch_size, SAMPLE_LEADING)

def estimate_val_fracs(prop, val, run, tech, var):
    fracs = get_fracs(prop, val, run)
#    write_fracs_dummy(fracs)
    return sample_frac_stats(fracs, tech, var, SAMPLE_LEADING)

def tech_label(technique, variable):
    return "%s_%s" % (technique, variable)

def update_data(run, exp, val, technique, variable, stats, actf, plot_data):
    exp_dict = plot_data[exp.name]
    val_dict = exp_dict[val.val]
    val_dict['style'] = run.display_style
    val_dict['actual'] = [np.array([stat["numhits"] for stat in stats]), np.array([actf]*len(stats))]
    lines = val_dict.get('lines', [])
    val_dict['lines'] = lines
    for key in KEYS:
        xs = np.array([stat["numhits"] for stat in stats])
        ys = np.array([stat[key+"_avg"] for stat in stats])            
        yerr = np.array([stat[key+"_std"] for stat in stats]) 
        bottom = np.array([stat[key+"_.025"] for stat in stats])            
        top = np.array([stat[key+"_.975"] for stat in stats])
        toperr = []
        for stat in stats:
            err = sorted(abs(actf - k) for k in stat[key+"_allkeys"])
            err = err[int(len(err)*.95)]
            toperr.append(err)
        toperr = np.array(toperr)
        lines.append([xs, ys, yerr, bottom, top, toperr, run.name+"_"+val.val+"_"+key, tech_label(technique, variable)])

def generate_plot(plot_data):
    all_vals = set()
    for exp, exp_dict in plot_data.items():
        for val, val_dict in exp_dict.items():
            all_vals.add(val)
            plot_val(exp, val, val_dict)
            plot_conf(exp, val, val_dict)
            plot_95err(exp, val, val_dict)
    for val in all_vals:
        to_plot = []
        for exp, exp_dict in plot_data.items():
            for v, val_dict in exp_dict.items():
                if val == v:
                    to_plot.append((exp, val_dict))
        plot_all(val, to_plot)

def line_label(run, technique):
    parts = run.split("_")
    val = run[-2]
    
    size=-1
    for part in parts:
        if part.startswith("size"):
            size = int(part[4:])
    if parts[1] == "male2":
        parts[1] = "male"
    dataset_item = parts[1].title()
    dataset_ammt = parts[2]
    if technique.startswith("batch"):
        tech = "LabelR"
        if 'noredundancy' in run:
            tech = "LabelNoR"
    elif technique.startswith("min"):
        tech = "Min"
    elif technique.startswith("simpleavg"):
        tech = "Avg"
    elif technique.startswith("weightedavg"):
        tech = "Thresh"
    else:
        raise Error("Unknown Technique: %s" % (technique))

    return "(%s=%s, %s %d)" % (dataset_item, dataset_ammt, tech, size)

def plot_all(val, to_plot):
    markers = ['-']*6 + ['--']*6#, '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    sub = plt.figure().add_subplot(111)
    for idx, to in enumerate(to_plot):
        exp, val_dict = to
#        xs, ys = val_dict['actual']
#        if idx == 0:
#            sub.plot(xs, ys, 'k-', label="Actual")
#        else:
#            sub.plot(xs, ys, 'k-')
        for line in sorted(val_dict['lines'], key=lambda x: 1-float(x[6].split("_")[2])):
            xs, ys, yerr, bottom, top, toperr, label, technique = line
            topbot = [p[0]-p[1] for p in zip(top, bottom)]
            fmt = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
        #        sub.errorbar(xs, ys, yerr=yerr, fmt=fmt, label=(label+"_"+technique)[-15:])
            sub.plot(xs, topbot, fmt, label=line_label(label, technique))
#            sub.plot(xs, bottom, fmt, label=line_label(label, technique))
#            sub.plot(xs, top, fmt)
        sub.legend(loc=0, prop={'size': 11})
#        sub.set_ylim((0,1))

        
    sub.set_ylim((0,.15))
    sub.set_xlabel("HITs completed")
    sub.set_ylabel("95% Confidence interval width")
#    sub.set_ylabel("Upper and lower 95% confidence intervals")
#    plt.suptitle('Estimating %% %s' % (val.title()))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def plot_val(exp, val, val_dict):
    markers = ['-']*6 + ['--']*6#, '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    xs, ys = val_dict['actual']
    sub = plt.figure().add_subplot(111)
    sub.plot(xs, ys, 'k-', label="Actual")
    for idx, line in enumerate(val_dict['lines']):
        xs, ys, yerr, bottom, top, toperr, label, technique = line
        fmt = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
#        sub.errorbar(xs, ys, yerr=yerr, fmt=fmt, label=(label+"_"+technique)[-15:])
        sub.plot(xs, bottom, fmt, label=line_label(label, technique))
        sub.plot(xs, top, fmt)
    sub.legend(loc=0, prop={'size': 11})
    sub.set_ylim((0,1))
    sub.set_xlabel("HITs completed")
    sub.set_ylabel("Upper and lower 95% confidence intervals")
#    plt.suptitle('Estimating %% %s' % (val.title()))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def plot_conf(exp, val, val_dict):
    markers = ['-']*6 + ['--']*6#, '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    sub = plt.figure().add_subplot(111)
    ci = [x/1000.0 for x in range(0, 200)]
    
    for idx, line in enumerate(val_dict['lines']):
        xs, ys, yerr, bottom, top, toperr, label, technique = line
        topbot = [p[0]-p[1] for p in zip(top, bottom)]
#        hits = []
#        print technique, len(top)
#        for i in ci:
#            diff = [abs(tb - i) for tb in topbot]
#            hits.append(xs[np.argmin(diff)])
        fmt = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
#        sub.errorbar(xs, ys, yerr=yerr, fmt=fmt, label=(label+"_"+technique)[-15:])
        sub.plot(xs, topbot, fmt, label=line_label(label, technique))

#        sub.plot(ci, hits, fmt, label=(label+"_"+technique)[-45:])
    sub.legend(loc=0, prop={'size': 11})
    sub.set_ylim((0,.15))
    sub.set_xlabel("HITs completed")
    sub.set_ylabel("95% Confidence interval width")
#    plt.suptitle('Estimating %% %s' % (val.title()))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def plot_95err(exp, val, val_dict):
    markers = ['-']*6 + ['--']*6#, '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    sub = plt.figure().add_subplot(111)
    ci = [x/1000.0 for x in range(0, 200)]
    
    for idx, line in enumerate(val_dict['lines']):
        xs, ys, yerr, bottom, top, toperr, label, technique = line
        fmt = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
        sub.plot(xs, toperr, fmt, label=line_label(label, technique))
    sub.legend(loc=0, prop={'size': 11})
    sub.set_ylim((0,.10))
    sub.set_xlabel("HITs completed")
    sub.set_ylabel("95% Percentile error")
#    plt.suptitle('Estimating %% %s' % (val.title()))
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

def estimate(run_name, plot_data):
    print "Run:", run_name
    run = ExpRun.objects.get(name=run_name)
    runvals = RunVal.objects.filter(run=run)
    exp = run.exp
    prop = exp.prop
    actual = load_dataset(exp.name)[3]
    empirical = get_empirical_dist(exp, actual)

    for val in runvals:
        if run.display_style == 'tile':
            for technique, variables in TECHNIQUES:
                for variable in variables:
                    stats = estimate_val_fracs(prop, val.val, run, technique, variable)
                    update_data(run, exp, val, technique, variable, stats, dict(empirical)[val.val], plot_data)
        elif run.display_style == 'batch':
            stats = estimate_val_values(prop, val.val, run)
            update_data(run, exp, val, "batch", "novar", stats, dict(empirical)[val.val], plot_data)
        else:
            raise Error("Unknown display style '%s'" % (run.display_style))


def technique_labels():
    tlabels = []
    for tech in TECHNIQUES:
        for var in tech[1]:
            tlabels.append(tech_label(tech[0], var))
    tlabels.append(tech_label("batch", "novar"))
    return tlabels

def error_header(tlabels):
    header = ["run"]
    for tl in tlabels:
        header.append("%s_%s" % (tl, "absolute"))
        header.append("%s_%s" % (tl, "relative"))
    return header

def print_errors(plot_data, outf):
    tlabels = technique_labels()
    headers = error_header(tlabels)
    with open(outf, "w") as outf:
        writer = DictWriter(outf, headers)
        writer.writeheader()
        for exp, exp_dict in plot_data.items():
            for val, val_dict in exp_dict.items():
                xs, ysact = val_dict['actual']
                runs = defaultdict(dict)
                # group run errors by run and technique
                for idx, line in enumerate(val_dict['lines']):
                    xs, ysline, yerr, bottom, top, toperr, label, technique = line
                    absolute = abs(ysact[-1] - ysline[-1])
                    relative = absolute/ysact[-1]
                    runs[label][technique] = (absolute, relative)
                # generate a row of output for each run
                for run, techniques in runs.items():
                    runrow = {'run': run}
                    for t, errs in techniques.items():
                        runrow["%s_%s" % (t, "absolute")] = errs[0]
                        runrow["%s_%s" % (t, "relative")] = errs[1]
                    writer.writerow(runrow)

if __name__ == '__main__':
    if DUMMY_CALC:
        fracs = get_fracs_dummy()
        print sample_frac_stats(fracs, "min", 1, SAMPLE_LEADING)[-1]
        sys.exit(0)
    
    if len(sys.argv) < 4:
        raise Exception("arguments: pdf_output technique_group run_names")
    pp = PdfPages(sys.argv[1]+".pdf")
    TECHNIQUES = TECH_COMBOS[sys.argv[2]]
    plot_data = defaultdict(lambda: defaultdict(dict))
    for run_name in sys.argv[3:]:
        estimate(run_name, plot_data)
    generate_plot(plot_data)
    print_errors(plot_data, sys.argv[1]+".csv")
    pp.close()
