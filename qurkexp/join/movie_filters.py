#!/usr/bin/env python
import sys, os
ROOT = os.path.abspath('%s/../..' % os.path.abspath(os.path.dirname(__file__)))
sys.path.append(ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'qurkexp.settings'
from django.core.management import setup_environ
from django.conf import settings
#setup_environ(settings)

from qurkexp.join.models import * 
from qurkexp.hitlayer.models import HitLayer

CANT_TELL = "can't tell/other"

def get_params():
    if len(sys.argv) < 5:
        print 'nscenes  batch|nobatch  runname  nassign'
        exit()
    
    num_celebs = int(sys.argv[1])
    if sys.argv[2] == "batch":
        batch = True
    elif sys.argv[2] == "nobatch":
        batch = False
    else:
        raise Exception("batch or no batch?")
    run_name = sys.argv[3]

    nassignments = int(sys.argv[4])
    
    return (num_celebs, batch, run_name, nassignments)

def gen_fvs(featurenames):
    fvs = [FeatureVal(name=n, order=i) for i,n in enumerate(featurenames)]
    for fv in fvs:
        fv.save()
    return fvs

def gen_feature(name, order, vals):
    f = Feature(name=name, order=order)
    f.save()
    for v in vals:
        f.vals.add(v)
    f.save()
    return f

def gen_features():
    features = [
        gen_feature("Number of people in scene", 0, gen_fvs(['0','1','2','3+',CANT_TELL]))
        ]

    for f in features:
        f.save()
    return features

def create_hits(c, nassignments):
    batch = c.experiment.batch
    for i, f in enumerate(c.experiment.features.all()):
       hitid = HitLayer.get_instance().create_job("/celeb/movie/features/%d/" % c.id,
                                             ('celeb_feature', [c.id]),
                                             desc = "Please select the number of actors in this movie scene.",
                                             title = "Count people (actors) in movie scene",
                                             price = 0.01,
                                             nassignments = nassignments)
       if c.experiment.batch:
           break

if __name__ == "__main__":
    (num_celebs, batch, run_name, nassignments) = get_params()
    features = gen_features()
    exp = FeatureExperiment(batch=batch, run_name=run_name)
    exp.save()
    for f in features:
        exp.features.add(f)
    exp.save()

    num_celebs = min(211, num_celebs)
    
    for i in range(1,num_celebs+1):
        c = FeatureCeleb(cid=i, image_set=0, experiment=exp)
        c.save()
        create_hits(c, nassignments)
