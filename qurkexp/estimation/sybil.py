"""
Generates two charts:
1) fraction of coordinated attackers vs. relative error for diff attack distances
2) hold constant attack distance, % gold standard vs. relative error for diff coordinated attackers

TODO: add step that removes a certain ammt of gold standard fraction from each response
Style points: see what happens if workers are uniform distance between correct and incorrect.
Style points: see what happens if bad workers answer more than 1 question each
Style points: see what happens if workers have larger response stdev
"""

from collections import defaultdict
from estimate_fractions import sample_frac_stats
from multiprocessing import Pool
import numpy
import random
import sys
import time

TECHNIQUES = [('simpleavg', [0]),
              ('weightedavg', [.85]),#[.75, .80, .85, .90, .95]),
              ('min', [1.1])]#[.10, .20, .30, .40, .50, .60, .70, .80, .90, 1, 1.1, 1.2, 1.3, 1.4, 1.5])]
DATA_DISTRO = [('class1', .5), ('class2', .5)]
SAMPLESIZE = 100
INCORRECT_ANSWERS = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
#INCORRECT_ANSWERS = [.8, .2]
GOLD_FRACTIONS = [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9]
#GOLD_FRACTIONS = [0, .1]
NUM_WORKERS = 30
ATTEMPTS = 50
CORRECT_STEPS = 3


# TODO: make a table of desired mean -> actual mean, and pick the actual mean
# so the user gets more accurate gold standard fractions
def boundednormal(x):
    if x == 0.0:
        return 0.0
    y = random.normalvariate(x, .2)
    if y < 0:
        return 0
    if y > .95:
        return .95
    return y

def bounded_dict(fractions):
    """
    Returns a dictionary mapping from fraction->dict, where
      dict['argfrac'] = the argument to boundednormal that results in the closest mean
        near that fraction
      dict['empmean'] = the empirical mean of boundednormal for that argument
    """
    sys.stderr.write("calculating optimal bounded normals\n")
    tics = [x/1000.0 for x in xrange(1000)]
    means = [numpy.mean([boundednormal(x) for idx in xrange(10000)]) for x in tics]
    mapping = {}
    for f in fractions:
        argmin = numpy.array([abs(x-f) for x in means]).argmin()
        mapping[f] = {'argfrac': tics[argmin], 'empmean': means[argmin]}
#    for g, a in mapping.items():
#        sys.stderr.write("%s, %s\n" % (g, str(a)))
    return mapping

def gen_data(data_distro):
    data = []
    for c,f in data_distro:
        data.extend([c]*int(10000*f))
    return data

# if correct, change samplesize to samplesize - goldsize
# need goldsize that's between 0 and 1, with avg = gold_ammounts (derichelet?)
# if val is negative, we'll discard the worker (spammer)
# if val is positive, we've at least spread out the spammers and left the 
#   correct workers constant
def gen_worker_val(correct, incorrect_val, data, samplesize, goldfrac):
    if correct:
        size = int(samplesize - (boundednormal(goldfrac)*samplesize))
        if size == 0:
            val = 0
        else:
            val = 1.0*len(filter(lambda x: x == 'class1', random.sample(data, size)))
            val /= size
    else:
        gold = boundednormal(goldfrac)
        val = incorrect_val - gold
        val /= 1.0-gold
    return val

# create 100 workers in two classes: a class that samples data
# distributed around some mean (e.g., .2) and a class that ignores the
# data and answers incorrect_val regardless
# if, after gold standard correction, the value returned is negative, we ignore
# this turker from the getgo
def gen_responses(num_workers, num_correct, incorrect_val, data, samplesize, goldfrac):
    resp = []
    for worker in xrange(num_workers):
        correct = worker < num_correct
        val = gen_worker_val(correct, incorrect_val, data, samplesize, goldfrac)
        if val >= 0:
            resp.append({'estf': val, 'user': str(worker)})
    return resp

def calculate_errors(data_distro, num_workers, incorrect_answers, samplesize, attempts, correct_steps, gold):
    """
    feed worker responses into the various fraction estimation techniques

    return dictionary of "technique_gold_incorrect->[[error*]]*" 
      where error is the absolute error of each attempt, and the list of lists is
      indexed by the number of correct answers
    """
    args = []
    correct_val = dict(data_distro)['class1']
    data = gen_data(data_distro)
    sys.stderr.write("Creating all experiments\n")
    for idx in xrange(attempts):
#        sys.stderr.write("Attempt %d\n" % (idx))
        for num_correct in xrange(correct_steps, num_workers+1, correct_steps):
            for incorrect_val in incorrect_answers:
                for goldmean, meaninfo in gold.items():
                    resp = gen_responses(num_workers, num_correct, incorrect_val, data, samplesize, meaninfo['argfrac'])
                    for technique, variables in TECHNIQUES:
                        for variable in variables:
                            key = "%s_%.3f_%.3f_%.3f" % (technique, variable, meaninfo['empmean'], incorrect_val)
                            args.append((key, num_correct, resp, technique, variable))

    starttime = time.time()
    pool = Pool(processes=8)
    results = pool.imap(run_sample, args)

    errors = defaultdict(lambda: defaultdict(list))
    idx = 0
    for key, num_correct, stats in results:
        errors[key][num_correct].append(stats[-1]['estf_avg'])
        if idx % 1000 == 0:
            sys.stderr.write("Finished: %s, %d/%d, %d\n" % (key, idx, len(args), time.time() - starttime))
        idx += 1
    return errors

def run_sample(arg_group):
    key, num_correct, resp, technique, variable = arg_group
    stats = sample_frac_stats(resp, technique, variable, False)
    # sys.stderr.write("buh? %s, %s\n" % (key, str(stats)))
    return (key, num_correct, stats)


# measure stats on mean and jackknifed 95% confidence interval
def output_errors(errors, num_workers):
    techniques = list(errors.keys())
    info = ["avg", "lower", "upper"]
    tech_labels = ["%s_%s" % (t, i) for t in techniques for i in info]
    labels = ["num_correct"]
    labels.extend(tech_labels)
    print ",".join(labels)
    for idx in xrange(num_workers+1):
        output = [idx]
        for t in techniques:
            if idx in errors[t]:
                error_list = errors[t][idx]
                error_list.sort()
                output.append(numpy.mean(error_list))
                output.append(error_list[int(len(error_list)*.025)])
                output.append(error_list[int(len(error_list)*.975)])
        if len(output) > 1:
            output = [str(o) for o in output]
            print ",".join(output)

if __name__ == "__main__":
    gold = bounded_dict(GOLD_FRACTIONS)
    errors = calculate_errors(DATA_DISTRO, NUM_WORKERS, INCORRECT_ANSWERS, SAMPLESIZE, ATTEMPTS, CORRECT_STEPS, gold)
    output_errors(errors, NUM_WORKERS)
