#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings

from qurkexp.join.models import * 
#setup_environ(settings)


def feature(run_name):
    if run_name == 'list':
        for exp in FeatureExperiment.objects.order_by('pk'):
            print exp.run_name
        return

    exp = FeatureExperiment.objects.get(run_name=run_name)
    print "<html><head></head><body style='font-size:20pt'>"
    
    for celeb in exp.featureceleb_set.order_by('cid'):
        anss = FeatureRespAns.objects.filter(fr__celeb=celeb)

        imgtmp = "http://wutang.csail.mit.edu:8000/media/images/scenes/%03d.jpg"
        
        print "<div><img width=300 src='%s'/> %s</div>" % (imgtmp%celeb.cid,
                                                          ','.join([x.val.name for x in anss]))
        
        #print celeb.cid, '\t',
        
    print "</body></html>"

def get_good_scenes(run_name):
    exp = FeatureExperiment.objects.get(run_name=run_name)
    cids = []
    for celeb in exp.featureceleb_set.order_by('cid'):
        anss = FeatureRespAns.objects.filter(fr__celeb=celeb)
        majvote = float(len([1 for x in anss if x.val.name == '1'])) / float(len(anss))
        if majvote > 0.5:
            cids.append(celeb.cid)
    return cids


def bpjoin_scenes(results, threshold=0.8):
    scenes = {}
    for taskid, vals in results:
        left, right = map(int, taskid.split('_'))
        tval = vals[-1][1]
        if left not in scenes: scenes[left] = []
        if tval > threshold:
            scenes[left].append((right, '%03f'%tval))
    return scenes
    

def bpjoin_print(scenes):
    print "<html><head></head><body style='font-size:20pt'>"
    imgtmp = "http://wutang.csail.mit.edu:8000/media/images/scenes/%03d.jpg"    
    for left, cids in scenes.items():
        #print left, cids
        print "<h1>Actor %s (%d)</h1>" % (left, len(cids))
        cids.sort(lambda x,y: x[1] < y[1] and 1 or -1)
        for (cid, prob) in cids:        
            print "<div><img width=300 src='%s'/>%s</div>" % (imgtmp%cid, prob)
    print "</body></html>"


def bpjoin_collect(run_names):
    triples = [] # task, worker, same?
    for run_name in run_names:
        exp = BPExperiment.objects.get(run_name=run_name)
        for ans in exp.get_answers():
            taskid = '%d_%d' % (ans.pair.left, ans.pair.right)
            wid = ans.bprm.wid
            same = ans.same
            triples.append((taskid, wid, same))
    return triples


def bpjoin_filter(triples):
    # find "bad" workers
    wcounts = {}
    wfalses = {}
    for tid, wid, res in triples:
        if wid not in wcounts:
            wcounts[wid] = 0
            wfalses[wid] = 0
        wcounts[wid] += 1
        if res:
            wfalses[wid] += 1
    badworkers = []
    print '<table>'
    for wid in wcounts:
        print '<tr><td>%s</td><td>%d</td><td>%d</td></tr>' % (wid, wcounts[wid], wfalses[wid])        
        if wfalses[wid] in [0, wcounts[wid]]:
            badworkers.append(wid)
    print '</table>'

    #print '<h1>bad workers</h1>'
    #for badworker in badworkers:


    # filter badworkers
    triples = filter(lambda x: x[1] not in badworkers, triples)



    return triples


    
def bpjoin(run_names):
    if 'list' in run_names:
        for exp in BPExperiment.objects.order_by('pk'):
            print exp.run_name
        return

    from gal import getbtjoindata, run_gal
    print run_names
    triples = bpjoin_collect(run_names)
    triples = bpjoin_filter(triples)
    workers, results = run_gal('btjoin', triples)
    scenes = bpjoin_scenes(results)
    bpjoin_print(scenes)
    return scenes
    

def get_actor_scenes(actorid, run_name):
    from gal import getbtjoindata, run_gal
    triples = bpjoin_collect([run_name])
    #triples = filter(lambda x: x[0].split('_')[0] == str(actorid), triples)
    workers, results = run_gal('btjoin', triples)
    scenes = bpjoin_scenes(results)
    return scenes[actorid]
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'python movie_results.py [feature|bpjoin] <run_name>'
        exit()

    exptype = sys.argv[1]
    runnames = sys.argv[2:]

    if exptype == 'feature':
        print len(get_good_scenes(runnames[0]))
        exit()
        feature(runnames[0])
    elif exptype == 'bpjoin':
        bpjoin(runnames)
    elif exptype == 'compare':
        compare(runnames)
    elif exptype == 'rate':
        rate(runnames)
    else:
        print "Could not recognize", runnames
# movie_all_naive_10_1
# movie_all_naive_5_1
# movie_all_smart_2_1
# movie_all_smart_3_1
# movie_all_smart_5_1
# movie_all_naive_5_2
# movie_all_naive_5_3
