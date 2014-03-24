#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats.stats import ss
from bestfit import regress, sigmoid

#setup_environ(settings)
from scipy import stats

def load(filename):
    xys = []
    for line in open(filename):
        ws = line.split()
        x = np.array(range(1,len(ws)))
        y = np.array(ws[1:], dtype='float')
        xys.append((ws[0], x, y))
    return xys

def print_trials(xys):
    print "w\ts\t-x0\tk"
    for name, x, y in xys:
        try:
            parts = name.split("_")
            x0, k = regress(x, y, 10000)
            print "%s\t%s\t%f\t%f" % (parts[0][1:], parts[1][1:], -x0, k)
        except RuntimeError, e:
            print e

def plot_trials(xys, wstring):
    markers = ['-', '--', '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    for idx, (name, x, y) in enumerate(xys):
        try:
            parts = name.split("_")
            xvals = np.array(range(80))
            if parts[0] == wstring:
                line = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
                x0, k = regress(x, y, 10000)
                plt.plot(xvals, sigmoid(xvals, x0, k), line, label=name)
        except RuntimeError, e:
            print e
    plt.legend()
    plt.savefig('figs/%s.png' % wstring, format='png')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "arguments: [filename with wi_sj lines]"
        sys.exit(-1)
    xys = load(sys.argv[1])
#    print_trials(xys)
    plot_trials(xys, "w5")
