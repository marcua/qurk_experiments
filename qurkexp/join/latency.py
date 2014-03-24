import sys,os
from datetime import datetime, timedelta
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.conf import settings
from qurkexp.join.models import *
from qurkexp.hitlayer.models import *

import pytz

def btjoin_resps(exp):
    return BPRespMeta.objects.filter(batch__experiment__run_name = exp)

def rate_resps(exp):
    return CompRespMeta.objects.filter(batch__experiment__run_name = exp)

def cmp_resps(exp):
    return CompRespMeta.objects.filter(batch__experiment__run_name = exp)

def feature_resps(exp):
    return FeatureRespMeta.objects.filter(celeb__experiment__run_name = exp)

def join_resps(exp):
    return PairResp.objects.filter(pair__run_name = exp)

def tot_time(start, end):
    delta = timedelta(hours=4, minutes=53) # we ran a hit and finished it fast, and this was the delta.
    totaltime = end-start-delta
    totaltime = (totaltime.days*24*3600.0 + totaltime.seconds)/3600.0
    return totaltime

def print_latency(exptype, exp):
    if exptype == 'btjoin':
        resps = btjoin_resps(exp)
    elif exptype == 'join':
        resps = join_resps(exp)
    elif exptype == 'feature':
        resps = feature_resps(exp)
    elif exptype == 'cmp':
        resps = cmp_resps(exp)
    elif exptype == 'rate':
        resps = rate_resps(exp)
    else:
        print "%s is not a valid experiment type" % exptype
        exit()
    
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
    print "%s\t%f\t%f\t%f" % (exp, tot_max, tot_95ptile, tot_50ptile)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'python latency.py [join|btjoin|feature|cmp|rate] [names]'
        exit()

    exptype = sys.argv[1]
    expnames = sys.argv[2:]
    for exp in expnames:
        print_latency(exptype, exp)
