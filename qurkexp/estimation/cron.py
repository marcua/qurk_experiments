import sys,os,base64,time,traceback
from datetime import datetime
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'

SLEEP_TIME = 0
cmds = [
#    'python generate_run.py gtav_male_.1_size150',
#    'python generate_run.py gtav_male_.1_size125',
#    'python generate_run.py gtav_male_.1_size150_2',
#    'python generate_run.py gtav_male_.1_size125_2',
#    'python generate_run.py gtav_male_.1_size100',
#    'python generate_run.py gtav_male_.1_size75',XXX
#    'python generate_run.py gtav_male_.1_size50',
#    'python generate_run.py gtav_male_.1_size25',
#    'python generate_run.py gtav_male_.1_size10',
#    'python generate_run.py gtav_male_.1_size5',
#    'python generate_run.py gtav_male_.1_batch_size10',
#    'python generate_run.py gtav_male_.1_batch_size10_noredundancy',
#    'python generate_run.py gtav_male_.1_batch_size5',XXX
#    'python generate_run.py gtav_male_.1_batch_size5_noredundancy',XXX
#    'python generate_run.py gtav_male_.1_batch_size20',
#    'python generate_run.py gtav_male_.1_batch_size20_noredundancy',
#    'python generate_run.py gtav_male_.1_batch_size15',
#    'python generate_run.py gtav_male_.1_batch_size15_noredundancy',
#    'python generate_run.py gtav_male_.01_size50',
#    'python generate_run.py gtav_male_.25_size50',
#    'python generate_run.py gtav_male_.5_size50',XXXX
#    'python generate_run.py gtav_male_.75_size50',
#    'python generate_run.py gtav_male_.9_size50',
#    'python generate_run.py gtav_male_.99_size50',
#    'python generate_run.py wgat_normal_batch_size20',
#    'python generate_run.py wgat_normal_batch_size20_noredundancy',
#    'python generate_run.py wgat_normal_batch_size5',
#    'python generate_run.py wgat_normal_batch_size5_noredundancy',
#    'python generate_run.py wgat_normal_size50',
#    'python generate_run.py wgat_normal_size25',
#    'python generate_run.py wgat_normal_size20',
#    'python generate_run.py shape_triangle_.1_size50',    
#    'python generate_run.py shape_yellowoutline_.1_size50',    
#    'python generate_run.py shape_triangle2_.1_size50',    
#    'python generate_run.py shape_yellowoutline2_.1_size50',    
#    'python generate_run.py wgat_normal_size50',
#    'python generate_run.py wgat_normal_size20',
#    'python generate_run.py wgat_normal_size5',
#    'python generate_run.py wgat_normal2_batch_size20_noredundancy',
#    'python generate_run.py wgat_normal2_batch_size5_noredundancy',
#    'python generate_run.py shape_triangle3_.1_size50',    
#    'python generate_run.py shape_yellowoutline3_.1_size50',    
#    'python generate_run.py gtav_male2_.01_size50',
#    'python generate_run.py gtav_male2_.1_size50',
#    'python generate_run.py gtav_male2_.25_size50',
#    'python generate_run.py gtav_male2_.5_size50',
#    'python generate_run.py gtav_male2_.75_size50',
#    'python generate_run.py gtav_male2_.9_size50',
#    'python generate_run.py gtav_male2_.99_size50',

#    'python generate_run.py gtav_male2_.01_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.1_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.5_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.9_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.99_batch_size20_noredundancy',

#    'python generate_run.py gtav_male2_.01_batch_size20',
#    'python generate_run.py gtav_male2_.1_batch_size20',
#    'python generate_run.py gtav_male2_.25_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.25_batch_size20',
#    'python generate_run.py gtav_male2_.5_batch_size20',
#    'python generate_run.py gtav_male2_.75_batch_size20_noredundancy',
#    'python generate_run.py gtav_male2_.75_batch_size20',
#    'python generate_run.py gtav_male2_.9_batch_size20',
#    'python generate_run.py gtav_male2_.99_batch_size20',

    #'python movie_batchpairs.py 211 5  naive movie_all_naive_5_1  5',
    ]
if __name__ == '__main__':
    from django.conf import settings
    from qurkexp.hitlayer.models import HitLayer, HIT
    from qurkexp.estimation.models import *
    hitlayer = HitLayer.get_instance()

    def gen_count_estimator(pk):
        try:
            rb = RunBatch.objects.get(id=pk)
        except Exception as e:
            print e
            print traceback.print_exc()
            return None

        def gen_est_responses(vrm, ans):
            for k,v in ans.items():
                parts = k.split("__")
                if len(parts) == 2 and parts[0] == "count":
                    ValRespAns.objects.create(vrm=vrm, val=parts[1], count=int(v))
                elif len(parts) == 2 and parts[0] == "value":
                    exp_item = ExpItem.objects.get(pk=int(parts[1]))
                    ValRespValue.objects.create(vrm=vrm, val=v, item=exp_item)
                elif len(parts) == 1 and parts[0] == "seconds_spent":
                    vrm.seconds_spent = float(v)
                    vrm.save()
                elif len(parts) == 1 and parts[0] == "screen_width":
                    vrm.screen_width = int(v)
                    vrm.save()
                elif len(parts) == 1 and parts[0] == "screen_height":
                    vrm.screen_height = int(v)
                    vrm.save()

        def f(hitid, allans):
            for ans in allans:
                vrm = ValRespMeta.objects.create(batch=rb,
                                aid = ans['purk_aid'],
                                wid = ans['purk_wid'],
                                hid = hitid,                                
                                accept_time = ans['purk_atime'],
                                submit_time = ans['purk_stime'])
                gen_est_responses(vrm, ans)
        return f

    hitlayer.register_cb_generator('estimate_counts', gen_count_estimator)

    def wait_hits():
        while HIT.objects.filter(done=False).count() > 0:
            HitLayer.get_instance().check_hits()
            print "going to sleep for %d sec" % (SLEEP_TIME)
            time.sleep(SLEEP_TIME)

    def runcmd(cmd):
        print cmd
        os.system(cmd)
        time.sleep(SLEEP_TIME)
        wait_hits()
    
    print "Ensuring all previous HITs are collected"
    wait_hits()

    while len(cmds) > 0:
        print "Running new command and collecting its hits"
        cmd = cmds.pop(0)
        runcmd(cmd)
