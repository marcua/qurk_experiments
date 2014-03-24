#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import *
from qurkexp.hitlayer.models import HitLayer
from scipy import stats

run_names = [
#            "test-ratings-4",
#            "squares-cmp-10-1-2-5-1", # compare 10 squares, batch 1, sort size 2, 5 assignments 1 cent each
#            "squares-cmp-10-1-5-5-1", # compare 10 squares, batch 1, sort size 5, 5 assignments 1 cent each
#            "squares-cmp-10-3-5-5-1", # compare 10 squares, batch 3, sort size 5, 5 assignments 1 cent each
#            "squares-rating-10-1-1-5-1", # compare 10 squares with rating, batch 1, 5 assignments 1 cent each
#            "squares-rating-10-3-1-5-1", # compare 10 squares with rating, batch 3, 5 assignments 1 cent each
#            "squares-rating-20-5-1-5-1", # compare 20 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-25-5-1-5-1", # compare 25 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-30-5-1-5-1", # compare 30 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-35-5-1-5-1", # compare 35 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-40-5-1-5-1", # compare 40 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-45-5-1-5-1", # compare 45 squares with rating, batch 5, 5 assignments 1 cent each
#            "squares-rating-50-5-1-5-1", # compare 50 squares with rating, batch 5, 5 assignments 1 cent each
            "squares-cmp-40-5-5-5-1", # compare 40 squares with sorting, batch size 5, sort size 5, 5 assignments 1 cent each
            "squares-cmp-40-5-5-5-2", # compare 40 squares with sorting, batch size 5, sort size 5, 5 assignments 1 cent each
#    "movie_cmp_1_1_5_5_v1", # compare adam's scenes with sorting, batch size 1, sort size 5, 5 assignments
#    "animals-saturn-cmp-1-5-5-1"
            ]

class UniqueIder():
    def __init__(self):
        self.id = 0
        self.map = {}
    def getid(self, key):
        try:
            retval = self.map[key]
        except:
            self.id += 1
            retval = self.id
            self.map[key] = retval
        return retval

def compare(v1, v2):
    if v1 > v2:
        return "gt"
    elif v2 > v1:
        return "lt"
    else:
        return "eq"

def get_sort_type(run_name):
    exp = CompExperiment.objects.get(run_name = run_name)
    return exp.sort_type

def handle_cmp(run_name, write_file):
    pair_results = {}
    cras = CompRespAns.objects.filter(crm__batch__experiment__run_name = run_name) 
    unique = UniqueIder()
    for cra in cras:
        if cra.v1.id >= cra.v2.id:
            raise Exception("Answers are in the top-right triangle of matrix")
        wid = unique.getid(cra.crm.wid)
        correct = compare(cra.v1.sortval, cra.v2.sortval)
        line = "%d\t%s\t%s\t%s\t%s\n" % (wid, cra.v1.data, cra.v2.data, correct, cra.comp)
        write_file.write(line)


if __name__ == "__main__":
    for run_name in run_names:
        f = open("sewoong-sort/%s" % (run_name), "w")
        f.write("wid\tleft\tright\tcorrectans\tworkerans\n")
        sort_type = get_sort_type(run_name)
        if sort_type == "cmp":
            handle_cmp(run_name, f)
        else:
            raise Exception("Can only dump comparisons at this point")
        f.close()
