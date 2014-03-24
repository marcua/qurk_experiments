import sys,os,base64,time,traceback
from datetime import datetime
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'


SLEEP_TIME = 10
if __name__ == '__main__':
    from django.conf import settings
    from qurkexp.hitlayer.models import HitLayer, HIT
    from qurkexp.join.models import *
    hitlayer = HitLayer.get_instance()

    def celeb_cb_generator(pid):
        try:
            pair = Pair.objects.get(pk=pid)
        except:
            return None

        def f(hitid, allans):
            for ans in allans:
                resp = PairResp(pair=pair,
                                aid = ans['purk_aid'],
                                wid = ans['purk_wid'],
                                hid = hitid,                                
                                accept_time = ans['purk_atime'],
                                submit_time = ans['purk_stime'],
                                same = ans['same'] == 'yes')
                resp.save()
                if ans['same'] == 'yes':
                    pair.yes += 1
                elif ans['same'] == 'no':
                    pair.no += 1
                pair.save()

        return f
    
    def celeb_features_cb_generator(pk):
        try:
            fc = FeatureCeleb.objects.get(id=pk)
        except Exception as e:
            print e
            print traceback.print_exc()
            return None
        def gen_feature_responses(fr, ans):
            for k,v in ans.items():
                parts = k.split("_")
                if len(parts) == 2 and parts[0] == "feature":
                    feature = Feature.objects.get(pk = int(parts[1]))
                    val = FeatureVal.objects.get(pk = int(v))
                    fra = FeatureRespAns(fr=fr,feature=feature,val=val)
                    fra.save()

        def f(hitid, allans):
            for ans in allans:
                fr = FeatureRespMeta(celeb=fc,
                                aid = ans['purk_aid'],
                                wid = ans['purk_wid'],
                                hid = hitid,                                
                                accept_time = ans['purk_atime'],
                                submit_time = ans['purk_stime'])
                fr.save()
                gen_feature_responses(fr, ans)
        return f



    
    def celeb_batchpair_cb_generator(bid):
        try:
            batch = BPBatch.objects.get(pk=bid)
        except Exception as e:
            print e
            print traceback.print_exc()
            return None

        def gen_batchpair_responses(bprm, ans):
            for k,v in ans.items():
                parts = k.split("_")
                if len(parts) == 3 and parts[0] == "radio":
                    left = int(parts[1])
                    right = int(parts[2])
                    pair = BPPair.objects.filter(bpbatch=bprm.batch).filter(left=left).get(right=right)
                    if v == "false":
                        same = False
                    elif v == "true":
                        same = True
                    else:
                        raise Exception("Incorrect radio value")
                    bpra = BPRespAns(bprm=bprm, pair=pair, same=same)
                    bpra.save()
                    #print "kv",k,v,same,bpra.same,bpra.id
            #print len(bprm.bprespans_set.all()), bprm.bprespans_set.all()[0].id, bprm.bprespans_set.all()[1].id

        def f(hitid, allans):
            for ans in allans:
                bprm = BPRespMeta(batch=batch,
                                aid = ans['purk_aid'],
                                wid = ans['purk_wid'],
                                hid = hitid,                                
                                accept_time = ans['purk_atime'],
                                submit_time = ans['purk_stime'])
                bprm.save()
                gen_batchpair_responses(bprm, ans)
        return f
    
    def sort_cb_generator(pk):
        try:
            cb = CompBatch.objects.get(id=pk)
        except Exception as e:
            print e
            print traceback.print_exc()
            return None
        def gen_comp_responses(crm, ans):
            sort_type = crm.batch.experiment.sort_type
            if sort_type == "cmp":
                for k,v in ans.items():
                    parts = k.split("_")
                    if len(parts) == 4 and parts[0] == "order":
                        v1 = CompVal.objects.get(pk=int(parts[2]))
                        v2 = CompVal.objects.get(pk=int(parts[3]))
                        cra = CompRespAns(crm=crm, v1=v1, v2=v2, comp=v)
                        cra.save()
            elif sort_type == "rating":
                for k,v in ans.items():
                    parts = k.split("_")
                    if len(parts) == 2 and parts[0] == "rate":
                        cv = CompVal.objects.get(pk=int(parts[1]))
                        rra = RateRespAns(crm=crm, val=cv, rating=int(v))
                        rra.save()
            else:
                raise Exception("Unknown sort type")

        def f(hitid, allans):
            for ans in allans:
                crm = CompRespMeta(batch=cb,
                                aid = ans['purk_aid'],
                                wid = ans['purk_wid'],
                                hid = hitid,                                
                                accept_time = ans['purk_atime'],
                                submit_time = ans['purk_stime'])
                crm.save()
                gen_comp_responses(crm, ans)
        return f

    hitlayer.register_cb_generator('celeb', celeb_cb_generator)
    hitlayer.register_cb_generator('celeb_feature', celeb_features_cb_generator)
    hitlayer.register_cb_generator('celeb_batchpair', celeb_batchpair_cb_generator)
    hitlayer.register_cb_generator('sort', sort_cb_generator)
    
    
    while True:
        HitLayer.get_instance().check_hits()
       
        print "going to sleep for %d sec" % (SLEEP_TIME)
        time.sleep(SLEEP_TIME)
    exit()
    cmds = [#'python movie_batchpairs.py 211 10 naive movie_all_naive_10_1 5',
            #'python movie_batchpairs.py 211 5  naive movie_all_naive_5_1  5',
            #'python movie_batchpairs.py 211 2  smart movie_all_smart_2_1  5',
            #'python movie_batchpairs.py 211 3  smart movie_all_smart_3_1  5',
            #'python movie_batchpairs.py 211 5  smart movie_all_smart_5_1  5',
            #'python generate_comparisons.py animals rating 27 5 1 5 animals-dangerous-rating-27-5-1-5-2',
        #'python movie_batchpairs.py 211 5  naive movie_all_naive_5_3 5',
        #'python generate_batchpairs.py 30 10 naive ordered 30-10-naive-ordered-20 5',
        #'python generate_batchpairs.py 30 5 naive ordered 30-5-naive-ordered-20 5',
        #'python generate_batchpairs.py 30 3 naive ordered 30-3-naive-ordered-20 5',
        #'python generate_comparisons.py squares cmp 40 1 10 5 squares-cmp-40-1-10-5-1'
#        'python generate_comparisons.py squares rating 50 5 1 5 squares-skew-rating-50-5-1-5-3',
#        'python generate_comparisons.py squares rating 50 5 1 5 squares-skew-rating-50-5-1-5-4',        
#        'python generate_comparisons.py squares cmp 40 1 5 5 squares-skew-cmp-40-1-5-5-1'
        #'python generate_comparisons.py squares rating 5 5 1 1 test_eugene_10',        
        ]

    

    def runcmds(cmds):
        for cmd in cmds:
            print cmd
            os.system(cmd)
        time.sleep(10)

        while HIT.objects.filter(done=False).count() > 0:
            HitLayer.get_instance().check_hits()
            print "going to sleep for %d sec" % (SLEEP_TIME)
            time.sleep(SLEEP_TIME)


    def runcmd(cmd):
        print cmd
        os.system(cmd)
        time.sleep(10)

        while HIT.objects.filter(done=False).count() > 0:
            HitLayer.get_instance().check_hits()
            print "going to sleep for %d sec" % (SLEEP_TIME)
            time.sleep(SLEEP_TIME)

    while len(cmds) > 0:
        cmd = cmds.pop(0)
        runcmd(cmd)
    exit()
    cmds = []
    for actorid in range(1, 5+1):
        cmds.append('python movie_comparisons.py cmp     movie_all_smart_3_1  %d 1 5 5 movie_cmp_%d_1_5_5_v3' % (actorid, actorid))
    runcmds(cmds)
    
    cmds = []
    for actorid in range(1, 5+1):
        cmds.append('python movie_comparisons.py rating  movie_all_smart_3_1  %d 5 1 5 movie_rat_%d_5_1_5_v3' % (actorid, actorid))
    runcmds(cmds)

