import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
pp = PdfPages('figs/sybil-renewed.pdf')
import matplotlib.pyplot as plt
matplotlib.rcParams['lines.linewidth'] = 3

from collections import defaultdict
import sys

def load(filename):
    plot_data = defaultdict(list)
    readf = open(filename)
    header = readf.readline().split(",")
    for line in readf:
        line_data = zip(header, map(float, line.split(",")))
        line_dict = defaultdict(dict)
        for exp, val in line_data[1:]:
            split = exp.rsplit("_", 1)
            tech, stat = split[0], split[1]
            line_dict[tech][stat] = val
            line_dict[tech]['num_correct'] = line_data[0][1]
        for tech, point in line_dict.items():
            plot_data[tech].append(point)
    return plot_data

def allowed_tech(tech, only_tech):
    for t in only_tech:
        if t in tech:
            return True
    return False

def allowed_dist(tech, only_dist):
    for d in only_dist:
        if d == float(tech.rsplit("_", 1)[1]):
            return True
    return False

def allowed_gold(tech, only_gold):
    for g in only_gold:
        if abs(g - float(tech.rsplit("_", 2)[1])) < .01:
            return True
    return False

def allowed(tech, only_tech, only_dist, only_gold):
    return allowed_tech(tech, only_tech) and allowed_dist(tech, only_dist) and allowed_gold(tech, only_gold)

def line_label(tech, display_gold):
    parts = tech.split("_")
    name = parts[0].title()
    dist = float(parts[-1])
    gold = float(parts[-2])
    if display_gold:
        return ("Attacker=%.2f, Gold=%.2f%%" % (dist, gold*100), (-dist, gold))
    else:
        return ("Attacker=%.2f" % (dist), (dist, gold))

def plot(data, only_techniques, only_distances, only_golds, display_gold):
    markers = ['--']*6 + ['-']*6 #, '-.', ',', 'o', 'v', '^', '>', '1', '*', ':']
    colors = ['b', 'g', 'r', 'c', 'm', 'y']
    idx = 0
    sub = plt.figure().add_subplot(111)
    sub.plot([x for x in range(0, 30)], [.5 for x in range(0, 30)], "k-", label="Actual")
    data = [(tech, line_label(tech, display_gold), points) for tech, points in data.items()]
    data = sorted(data, key=lambda p: p[1][1])
    for tech, label, points in data:
        if not allowed(tech, only_techniques, only_distances, only_golds):
            continue
        correct = [p['num_correct'] for p in points]
        max_correct = max(correct)
        xs = [max_correct - c for c in correct]
        ys = [p['avg'] for p in points]
        fmt = '%s%s' % (colors[idx % len(colors)], markers[idx % len(markers)])
#        sub.scatter(xs, ys, color=colors[idx % len(colors)], label=label[1])
        sub.plot(xs, ys, fmt, label=label[0])
        idx += 1
    sub.legend(loc=0, prop={'size': 9 if display_gold else 11})
    sub.set_ylim((0,1.1))
    sub.set_xlabel("Number of coordinated attackers")
    sub.set_ylabel("Mean estimated fraction")
    plt.savefig(pp, format='pdf')
    plt.cla()
    plt.clf()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "arguments: input_csv"
        sys.exit(-1)
    print "Remember: NUM_WORKERS should be a multiple of CORRECT_STEPS"
    plot_data = load(sys.argv[1])
    plot(plot_data, ['weightedavg'], [.1, .2, .3, .4, .5, .6, .7, .8, .9], [0], False)
    plot(plot_data, ['weightedavg'], [.9, .1], [0.0, .1, .3, .5, .7, .9], True)
#    plot(plot_data, ['wa'], [.4], [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9])
#    plot(plot_data, ['wa'], [.6], [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9])
#    plot(plot_data, ['wa'], [.9], [0.0, .1, .2, .3, .4, .5, .6, .7, .8, .9])
#    plot(plot_data, ['weightedavg'], [0, .1, .5, .8], [0])
#    plot(plot_data, ['simpleavg'], [0, .1, .5, .8], [0])
#    plot(plot_data, ['min', 'weightedavg', 'simpleavg'], [.5], [0])
#    plot(plot_data, ['weightedavg'], [.5], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['min'], [.5], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['weightedavg'], [.8], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['min'], [.8], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['min'], [.2], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['min'], [.1], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['min'], [0], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['simpleavg'], [.8], [0, .1, .3, .5, .7, .9])
#    plot(plot_data, ['simpleavg'], [0], [0, .1, .3, .5, .7, .9])
    pp.close()
