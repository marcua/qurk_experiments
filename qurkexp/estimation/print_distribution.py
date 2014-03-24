import django_includes
import sys

from qurkexp.estimation.datasets import load_dataset, print_empirical_dist
from qurkexp.estimation.models import *

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("arguments: [run_name from datasets.py]")
    args = load_dataset(sys.argv[1])
    exp = EstExp.objects.get(name=sys.argv[1])
    print_empirical_dist(exp, args[3])
