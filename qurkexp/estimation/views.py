import random
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext, loader
from django.conf import settings
from django.db.models import F

from qurkexp.hitlayer.settings import SANDBOX

from qurkexp.estimation.models import *

def item_html(item):
    if item.kind.name == "shape":
        return """<img src='%s' class="item" />""" % (item.data)
    elif item.kind.name == "gtav":
        return """<img src='%s' class="item" />""" % (item.data)
    elif item.kind.name == "wgat":
        return """<div class="tweet" />%s</a></div>""" % (item.data.rstrip("</a").rstrip("</").rstrip("<").replace("<!--",''))
    else:
        raise Exception("Unknown item kind: %s" % (item.kind.name))


WGAT_CATEGORIES = {"IS":"Information Sharing (e.g., sharing an article about baking)",
              "SP":"Self-Promotion (e.g., sharing author's own work)",
              "OC":"Opinion / Complaint (e.g., 'I hate product X!')",
              "RT":"Random Thought (e.g., 'Summer really is hot')",
              "ME":"Me Now (e.g., 'Just finished cleaning!')",
              "QF":"Question to Followers (e.g., 'Do any of you work on weekends?')",
              "PM":"Presence Maintenance (e.g., 'Hello everyone!')",
              "CONV":"Conversation (e.g., responding to a friend)"}

def property_dict(kind, prop, val):
    if kind.name == "shape":
        rdict = {'value':val, 'human_value': val}
        if prop == "fill":
            rdict['question'] = "have a <u>%s</u> fill color" % (val)
        elif prop == "outline":
            rdict['question'] = "have a <u>%s</u> outline color" % (val)
        elif prop == "shape":
            rdict['question'] = "are <u>%s</u>" % (val)
        else:
            raise Error("Unknown property: %s" % (prop))
        return rdict
    elif kind.name == "gtav":
        rdict = {'value':val, 'human_value': val}
        if prop == "gender":
            rdict['question'] = "are <u>%s</u>" % (val)
        else:
            raise Error("Unknown property: %s" % (prop))
        return rdict
    elif kind.name == "wgat":
        rdict = {'value':val}
        if prop == "category":
            rdict['question'] = "is about <u>%s</u>" % (WGAT_CATEGORIES[val])
            rdict['human_value'] = WGAT_CATEGORIES[val] + "<br>"
        else:
            raise Error("Unknown property: %s" % (prop))
        return rdict
    else:
        raise Error("Unknown item kind: %s" % (kind.name))

def plural_type(kind):
    if kind.name == "shape":
        return ("shapes", "shapes")
    elif kind.name == "gtav":
        return ("people", "people")
    elif kind.name == "wgat":
        return ("tweets (messages from people on the Twitter social network)", "tweets")
    else:
        raise Error("Unknown item kind: %s" % (kind.name))

def singular_type(kind):
    if kind.name == "shape":
        return "shape"
    elif kind.name == "gtav":
        return "person"
    elif kind.name == "wgat":
        return "tweet"
    else:
        raise Error("Unknown item kind: %s" % (kind.name))

def counts(request, pk):
    try:
        rb = RunBatch.objects.filter(pk=pk)[0]
    except ObjectDoesNotExist:
        return redirect("/estimate/sorry")

#    hitid = request.REQUEST.get('hitId', None)
#    assignmentid = request.REQUEST.get('assignmentId', None)
#    workerid = request.REQUEST.get('workerId', None)

    items = list(ExpItem.objects.filter(batches = rb))
    #items = Item.objects.filter(exp_ptrs__batches = rb))
    random.shuffle(items)
    vals = RunVal.objects.filter(run__batches = rb)
    exp = EstExp.objects.get(runs__batches = rb)
    rdict = {
        'batch': [(item.pk, item_html(item.item)) for item in items],
        'plural_type': plural_type(exp.kind),
        'singular_type': singular_type(exp.kind),
        'num_items': len(items),
        'sandbox': SANDBOX,
        'property': exp.prop,
        'properties': [property_dict(exp.kind, exp.prop, rv.val) for rv in vals]
    }

    style = rb.run.display_style
    if style == "tile":
        return render_to_response("estimation/simplecount.html", rdict)
    elif style == "batch":
        return render_to_response("estimation/simplebatch.html", rdict)
    else:
        raise Error("Unknown display style: %s" % (style))

def sorry(request):
    return render_to_response("estimation/sorry.html")
