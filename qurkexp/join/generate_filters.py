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
    num_celebs = int(sys.argv[1])
    if sys.argv[2] == "batch":
        batch = True
    elif sys.argv[2] == "nobatch":
        batch = False
    else:
        raise Exception("batch or no batch?")
    run_name = sys.argv[3]
    return (num_celebs, batch, run_name)

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
        gen_feature("Gender", 0, gen_fvs(["male", "female", CANT_TELL])),
        gen_feature("Hair Color", 1, gen_fvs(["brown/black", "blond", "white", "red", CANT_TELL])),
        gen_feature("Skin Color", 2, gen_fvs(["white", "black", CANT_TELL]))]
    for f in features:
        f.save()
    return features

def create_hits(c):
    batch = c.experiment.batch
    for i, f in enumerate(c.experiment.features.all()):
       hitid = HitLayer.get_instance().create_job("/celeb/features/%d/%d" % (c.id, i),
                                             ('celeb_feature', [c.id]),
                                             desc = "Look at a picture of a celebrity and identify thier gender, hair, or skin features.",
                                             title = "Identify celebrity features",
                                             price = 0.01,
                                             nassignments = 5)
       if c.experiment.batch:
           break

if __name__ == "__main__":
    (num_celebs, batch, run_name) = get_params()
    features = gen_features()
    exp = FeatureExperiment(batch=batch, run_name=run_name)
    exp.save()
    for f in features:
        exp.features.add(f)
    exp.save()
    
    for j in [1,2]:
        for i in range(1,num_celebs+1):
            c = FeatureCeleb(cid=i, image_set=j, experiment=exp)
            c.save()
            create_hits(c)
