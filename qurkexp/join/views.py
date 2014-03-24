import random
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader
from django.conf import settings
from django.db.models import F

from qurkexp.hitlayer.settings import SANDBOX

from qurkexp.join.models import *
from qurkexp.join.generate_filters import CANT_TELL

def turk_pair(request, pk):
    try:
        pair = Pair.objects.get(pk=pk)
    except:
        return redirect("/celeb/sorry")


    hitid = request.REQUEST.get('hitId', None)
    assignmentid = request.REQUEST.get('assignmentId', None)
    workerid = request.REQUEST.get('workerId', None)

    a = Access(pair=pair,
               aid=assignmentid,
               wid=workerid,
               hid=hitid,
               preview = assignmentid == "ASSIGNMENT_ID_NOT_AVAILABLE")
    a.save()
    
    return render_to_response("celeb/turk_pair.html", {"pair": pair, 'sandbox':SANDBOX})

def features(request, pk, fid):
    try:
        fc = FeatureCeleb.objects.get(pk=pk)
    except:
        return redirect("/celeb/sorry")


    hitid = request.REQUEST.get('hitId', None)
    assignmentid = request.REQUEST.get('assignmentId', None)
    workerid = request.REQUEST.get('workerId', None)

    a = FeatureAccess(celeb=fc,
               aid=assignmentid,
               wid=workerid,
               hid=hitid,
               featurenum=fid,
               preview = assignmentid == "ASSIGNMENT_ID_NOT_AVAILABLE")
    a.save()

    features = Feature.objects.filter(featureexperiment = fc.experiment).filter(order=fid)
    if fc.experiment.batch:
        features = Feature.objects.filter(featureexperiment = fc.experiment).order_by("order")
    display_features = []
    for f in features:
        # don't save the new val ordering---it's just for display
        display_features.append({"feature": f, "vals": sorted(f.vals.all(), key=lambda fv: fv.order)})
    return render_to_response("celeb/celeb_features.html", {"celeb": fc, "features":display_features, "sandbox":SANDBOX, "cant_tell": CANT_TELL})




def movie_features(request, pk, fid=0):
    try:
        fc = FeatureCeleb.objects.get(pk=pk)
    except:
        return redirect("/celeb/sorry")


    hitid = request.REQUEST.get('hitId', None)
    assignmentid = request.REQUEST.get('assignmentId', None)
    workerid = request.REQUEST.get('workerId', None)

    a = FeatureAccess(celeb=fc,
               aid=assignmentid,
               wid=workerid,
               hid=hitid,
               featurenum=fid,
               preview = assignmentid == "ASSIGNMENT_ID_NOT_AVAILABLE")
    a.save()

    features = Feature.objects.filter(featureexperiment = fc.experiment).filter(order=fid)
    if fc.experiment.batch:
        features = Feature.objects.filter(featureexperiment = fc.experiment).order_by("order")
    display_features = []
    for f in features:
        # don't save the new val ordering---it's just for display
        display_features.append({"feature": f, "vals": sorted(f.vals.all(), key=lambda fv: fv.order)})
    return render_to_response("celeb/movie_features.html",
                              {"celeb": fc, "features":display_features, "sandbox":SANDBOX, "cant_tell": CANT_TELL,
                               "imgurl" : '%03d' % fc.cid})



def sorry(request):
    return render_to_response("celeb/sorry.html")



def superjoin(request, bid):
    try:
        batch = BPBatch.objects.get(pk=bid)
    except:
        batch = None


    try:
        aid=request.REQUEST.get('assignmentId', None)
        access = BPAccess(batch=batch,
                          aid=aid,
                          hid=request.REQUEST.get('hitId', None),
                          wid=request.REQUEST.get('workerId', None),
                          preview=(aid == 'ASSIGNMENT_ID_NOT_AVAILABLE'))
        access.save()
    except:
        pass

        
    if not batch:
        urltemp = "http://people.csail.mit.edu/marcua/experiments/join/%d/%d.jpg"
        lefts = []
        rights = []
        for i in xrange(5):
            lefts.append({'url' : urltemp % (1, i+1), 'pk' : i})
            rights.append({'url' : urltemp % (2, i+1), 'pk' : i + 10})

        return render_to_response('celeb/sorry.html')
            
        return render_to_response("celeb/batch_pair.html",
                                  {"lefts": lefts,
                                   "rights":rights},
                                  context_instance = RequestContext(request))
    elif batch.experiment.smart_interface:
        urltemp = "http://people.csail.mit.edu/marcua/experiments/join/%d/%d.jpg"        
        lefts = set()
        rights = set()
        for p in batch.pairs.all():
            lefts.add(p.left)
            rights.add(p.right)
        lefts = [{'url' : urltemp % (1, x), 'pk' : x} for x in lefts]
        rights = [{'url' : urltemp % (2, x), 'pk' : x} for x in rights]
        random.seed(0)
        random.shuffle(lefts)
        random.shuffle(rights)

        return render_to_response("celeb/batch_pair.html",
                                  {"lefts": lefts,
                                   "rights":rights},
                                  context_instance = RequestContext(request))
    else:
        return render_to_response("celeb/batch_pair_naive.html",
                                  {'pairs': batch.pairs.all()}, 
                                  context_instance = RequestContext(request))





def movie_superjoin(request, bid):
    try:
        batch = BPBatch.objects.get(pk=bid)
    except:
        batch = None

    try:
        aid=request.REQUEST.get('assignmentId', None)
        access = BPAccess(batch=batch,
                          aid=aid,
                          hid=request.REQUEST.get('hitId', None),
                          wid=request.REQUEST.get('workerId', None),
                          preview=(aid == 'ASSIGNMENT_ID_NOT_AVAILABLE'))
        access.save()
    except:
        pass


    
    lurltemp = "http://wutang.csail.mit.edu:8000/media/images/%s/%d.jpg"
    rurltemp = "http://wutang.csail.mit.edu:8000/media/images/%s/%03d.jpg"        

    if not batch:
        lefts = []
        rights = []
        for i in xrange(5):
            lefts.append({'url' : lurltemp % ('actors', i+1), 'pk' : i})
            rights.append({'url' : rurltemp % ('scenes', i+1), 'pk' : (i * 13) % 211})
        print 'preview HIT'
        print lefts
        print rights

        return render_to_response('celeb/sorry.html')
            
        return render_to_response("celeb/batch_pair.html",
                                  {"lefts": lefts,
                                   "rights":rights},
                                  context_instance = RequestContext(request))

    elif batch.experiment.smart_interface:
        lefts = set()
        rights = set()
        for p in batch.pairs.all():
            lefts.add(p.left)
            rights.add(p.right)
        print lefts, rights
        lefts = [{'url' : lurltemp % ('actors', x), 'pk' : x} for x in lefts]
        rights = [{'url' : rurltemp % ('scenes', x), 'pk' : x} for x in rights]
        random.seed(0)
        random.shuffle(lefts)
        random.shuffle(rights)

        return render_to_response("celeb/movie_batch_pair.html",
                                  {"lefts": lefts,
                                   "rights":rights},
                                  context_instance = RequestContext(request))
    else:
        pairs = []
        for p in batch.pairs.all():
            print p.left, p.right
            d = {'left' : p.left,
                 'right' : p.right,
                 'lurl' : lurltemp % ('actors', p.left),
                 'rurl' : rurltemp % ('scenes', p.right)
                }
            pairs.append(d)
                          
        return render_to_response("celeb/movie_batch_pair_naive.html",
                                  {'pairs': pairs},
                                  context_instance = RequestContext(request))




def type_terms(item_type):
    if item_type == "squares":
        terms = {"singular":"square", "plural":"squares", "feature":"size", "least":"smallest", "most":"largest"}
    elif item_type == "animals":
#        terms = {"singular":"animal", "plural":"animals", "feature":"full adult size", "least":"smallest", "most":"largest"}
        terms = {"singular":"animal", "plural":"animals", "feature":"likelihood to appear on the planet Saturn", "least":"least likely", "most":"most likely"}
#        terms = {"singular":"animal", "plural":"animals", "feature":"dangerousness", "least":"least dangerous", "most":"most dangerous"}
    elif item_type.startswith("movie_"):
        terms = {"singular" : "scene",
                 "plural" : "scenes",
                 "feature" : "flatteringness",
                 "least" : "least flattering",
                 "most" : "most flattering"} # ewu
    else:
        raise Exception("Unexpected item_type")
    return terms


def sort(request, bid):
    try:
        batch = CompBatch.objects.get(pk=bid)
    except:
        raise Exception("Bad batch id")
    if batch.experiment.sort_type == "cmp":
        max_len = max(group.vals.all().count() for group in batch.compgroup_set.all())
        item_type = batch.experiment.item_type
        groups = []
        hidden_comparators = []
        for group in batch.compgroup_set.all():
            groups.append((group.id, [(v.id, v.to_html(item_type)) for v in group.vals.all()]))
            random.shuffle(groups[-1][1])
            for val1 in group.vals.all():
                for val2 in group.vals.all():
                    if val1.id < val2.id:
                        hidden_comparators.append("order_%d_%d_%d" % (group.id, val1.id, val2.id))
        terms = type_terms(item_type)
        return render_to_response("sort/cmp-saturn.html",
                                  {
                                    'groups': groups,
                                    'group_len': len(groups),
                                    'item_type': item_type,
                                    'max_len': max_len,
                                    'terms': terms,
                                    'sandbox': SANDBOX,
                                    'hidden_comparators': hidden_comparators,
                                  }, 
                                  context_instance = RequestContext(request)) 
    elif batch.experiment.sort_type == "rating":
        item_type = batch.experiment.item_type
        groups = []
        for group in batch.compgroup_set.all():
            groups.append((group.id, [(v.id, v.to_html(item_type)) for v in group.vals.all()]))
            random.shuffle(groups[-1][1])
        examples = CompVal.objects.filter(compgroup__batch__experiment = batch.experiment).distinct()
        examples = [v.to_html_preview(item_type) for v in random.sample(examples, min(10, len(examples)))]
        terms = type_terms(item_type)
        return render_to_response("sort/rating-saturn.html",
                                  {
                                    'groups': groups,
                                    'group_len': len(groups),
                                    'item_type': item_type,
                                    'sandbox': SANDBOX,
                                    'terms': terms,
                                    'examples': examples,
                                  }, 
                                  context_instance = RequestContext(request))
    else:
        raise Exception("Sort type not defined")





