#!/usr/bin/env python
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats.stats import ss

#setup_environ(settings)
from scipy import stats

def sigmoid(x, x0, k):
     y = 1 / (1 + np.exp(-k*(x-x0)))
     return y

def regress(x, y, howmuch):
    # polynomials don't work that well
    #    p1 = np.poly1d(np.polyfit(x[:howmuch],y[:howmuch],1))
    #    p2 = np.poly1d(np.polyfit(x[:howmuch],y[:howmuch],2))
    #    p3 = np.poly1d(np.polyfit(x[:howmuch],y[:howmuch],3))

    # sigmoid of the form 1/(1+e^(-k*(x-x0))), so we can change its slope 
    # (k) and intercept (x0)
    popt, pcov = curve_fit(sigmoid, x[:howmuch], y[:howmuch])
    return popt

def plot(x, y, popt):
    xp = np.linspace(0, 100, 1000)
    plt.plot(x, y, 'ro', xp, sigmoid(xp, *popt), 'b-')
    plt.ylim(.8,1.05)
    plt.show()

def sum_squared_error(x, y, popt):
    yprime = sigmoid(x, *popt)
    return ss(y-yprime)

def load(filename):
    vals = [float(x) for x in open(filename).readlines()]
    y = np.array(vals)
    x = np.array(xrange(0, len(vals)))
    return x,y

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "arguments: filename to do regression on"
        sys.exit(-1)
    x,y = load(sys.argv[1])
    plot(x, y, regress(x, y, 40))
    for i in [5, 10, 20, 30, 40, 50, 60, 70, 75]:
        print i, sum_squared_error(x, y, regress(x, y, i))
