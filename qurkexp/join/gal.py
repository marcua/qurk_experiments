import sys,os
from datetime import datetime
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.conf import settings
from qurkexp.join.models import *

def getjoindata(expnames):
    data = []
    for ename in expnames:
        if ename == 'list':
            runset = set()
            for e in Pair.objects.all():
                runset.add(e.run_name)
            continue

        for ans in PairResp.objects.filter(pair__run_name = ename):
            data.append(['%d_%d' % (ans.pair.left, ans.pair.right), ans.wid, ans.same])
    return data

def getbtjoindata(expnames):
    data = []
    for ename in expnames:
        if ename == 'list':
            for e in BPExperiment.objects.all():
                print e.run_name
            continue


        exp = BPExperiment.objects.get(run_name=ename)
        for ans in BPRespAns.objects.filter(bprm__batch__experiment = exp):
            meta = ans.bprm
            pair = ans.pair
            data.append(['%d_%d' % (pair.left, pair.right), meta.wid, ans.same])
    return data

def getfeaturedata(expnames):
    data = []
    for ename in expnames:
        if ename == 'list':
            for e in FeatureExperiment.objects.all():
                print e.run_name
            continue

        exp = FeatureExperiment.objects.get(run_name=ename)
        for ans in FeatureRespAns.objects.filter(fr__celeb__experiment__run_name=ename):
            meta = ans.fr
            celeb = ans.fr.celeb
            print celeb.cid, ans.feature.pk, ans.val.order
            data.append(['%d_%d' % (celeb.cid, ans.feature.pk), meta.wid, ans.val.order])
    return data


def getcompdata(expnames):
    data = []
    for ename in expnames:
        if ename == 'list':
            for e in CompExperiment.objects.all():
                if CompRespAns.objects.filter(crm__batch__experiment=e).count() > 0:
                    print e.run_name
            continue

        exp = CompExperiment.objects.get(run_name=ename)
        for ans in CompRespAns.objects.filter(crm__batch__experiment__run_name=ename):
            meta = ans.crm
            data.append(['%s_%s' % (ans.v1.data, ans.v2.data), meta.wid, ans.comp])
    return data


def getratedata(expnames):
    data = []
    for ename in expnames:
        if ename == 'list':
            for e in CompExperiment.objects.all():
                if RateRespAns.objects.filter(crm__batch__experiment=e).count() > 0:
                    print e.run_name
            continue


        exp = CompExperiment.objects.get(run_name=ename)
        for ans in RateRespAns.objects.filter(crm__batch__experiment__run_name=ename):
            meta = ans.crm
            data.append([str(ans.val.data), meta.wid, ans.rating])
    return data


def run_gal(exptype, data):
    """
    returns [spammers, results]
    spammers: [workerid, error]*
    results:  [taskid, [(val, prob)*]]
    """
    toinputfile(data)
    runit(exptype)
    spammers = getspammers()
    results = getmajvotes()
    return spammers, results
    

def toinputfile(data):
    """
    data is: [(task, workerid, result)*]
    """
    f = file('%s/java/inputfile' % settings.ROOT, 'w')
    for task, wid, result in data:
        f.write('%s\t%s\t%s\n' % (wid, task, result))
    f.close()

def runit(exptype):
    args = [settings.ROOT]*4
    args.append(exptype)
    print "/usr/bin/java -jar %s/java/gal.jar %s/java/inputfile %s/java/correctfile %s/java/costfile_%s 5" % tuple(args)
    os.system("/usr/bin/java -jar %s/java/gal.jar %s/java/inputfile %s/java/correctfile %s/java/costfile_%s 5" % tuple(args))


def getspammers():
    f = file('./data/worker-error-rates.txt', 'r')
    workers = []
    for l in f:
        l = l.strip()
        if l == '': continue
        if ': ' in l:
            val = map(lambda x: x.strip(), l.strip().split(":"))[1]            
        if 'Worker' in l:
            workers.append([val])
        elif 'Error' in l:
            workers[-1].append(float(val[:-1]))

    return workers

    

def getmajvotes():
    f = file('./data/object-probabilities.txt' , 'r')
    res = []
    for l in f:
        arr = tuple(l.strip().split('\t')[:3])
        task = arr[0]
        rest = arr[1:]
        #rest = '\t'.join(arr[1:])
        rest = map(lambda x: x.split('='), rest)
        rest = map(lambda x: (x[0][3:-1], float(x[1])), rest)
        #res.append((task, float(posval.split('=')[-1])))
        res.append((task, rest))
    return res



def gencostfiles():
    f = file('%s/java/costfile_btjoin'% settings.ROOT, 'w')
    f.write('True\tTrue\t0\n')
    f.write('False\tFalse\t0\n')
    f.write('True\tFalse\t2\n')
    f.write('False\tTrue\t1\n')
    f.close()
    
    f = file('%s/java/costfile_join'% settings.ROOT, 'w')
    f.write('True\tTrue\t0\n')
    f.write('False\tFalse\t0\n')
    f.write('True\tFalse\t2\n')
    f.write('False\tTrue\t1\n')
    f.close()

    f = file('%s/java/costfile_feature'% settings.ROOT, 'w')
    for i in xrange(6):
        for j in xrange(6):
            if i == j:
                f.write('%d\t%d\t0\n' % (i,j))
            else:
                f.write('%d\t%d\t1\n' % (i,j))                
    f.close()


    classes = ['gt', 'lt']
    f = file('%s/java/costfile_comp'% settings.ROOT, 'w')
    for i in classes:
        for j in classes:
            if i == j:
                f.write('%s\t%s\t0\n' % (i,j))
            else:
                f.write('%s\t%s\t1\n' % (i,j))                
    f.close()



    f = file('%s/java/costfile_rate' % settings.ROOT, 'w')
    for i in classes:
        for j in classes:
            if i == j:
                f.write('%s\t%s\t0\n' % (i,j))
            else:
                f.write('%s\t%s\t1\n' % (i,j))                
    f.close()





if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'python gal.py [join|btjoin|feature|comp|rate] [names]'
        exit()

    gencostfiles()
    #exit()

    exptype = sys.argv[1]
    expnames = sys.argv[2:]
    data = None
    if exptype == 'btjoin':
        data = getbtjoindata(expnames)
    elif exptype == 'join':
        data = getjoindata(expnames)
    elif exptype == 'feature':
        data = getfeaturedata(expnames)
    elif exptype == 'comp':
        data = getcompdata(expnames)
    elif exptype == 'rate':
        data = getratedata(expnames)
    else:
        print "%s is not a valid experiment type" % exptype
        exit()
    if not data:
        print 'please select 1+ experiment names'
        exit()

    workers, results = run_gal(exptype, data)
    for w in workers:
        print w
    for r in results:
        print r[0], '\t', r[1]
