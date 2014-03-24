from django.db import models, connection
from qurkexp.join.animals import animals_dict

connection.cursor().execute("SET search_path TO qurkexp, public")

# Comparator logic
class CompVal(models.Model):
    sortval = models.BigIntegerField()
    data = models.TextField()
    def to_html(self, item_type):
        if item_type == "squares":
            return """<div class="square" size="%s"></div>""" % (self.data)
        elif item_type == "animals":
            return """<img src="http://wutang.csail.mit.edu:8000/media/images/animals/%s.jpg" class="animal" /><br>%s""" % (self.data, animals_dict[self.data])
        elif item_type.startswith('movie_'):
            imgsrc = "http://wutang.csail.mit.edu:8000/media/images/scenes/%03d.jpg" % int(self.data)
            return """<img width=300 src="%s" class="movie" />""" % imgsrc
        else:
            raise Exception("unrecognized item type")

    def to_html_preview(self, item_type):
        if item_type.startswith('movie_'):
            imgsrc = "http://wutang.csail.mit.edu:8000/media/images/scenes/%03d.jpg" % int(self.data)
            return """<img width=150 src="%s" class="movie" />""" % imgsrc
        return self.to_html(item_type)

class CompExperiment(models.Model):
    run_name = models.TextField(unique=True)
    sort_size = models.IntegerField() # How many items to compare at once
    batch_size = models.IntegerField() # How many item comparisons to do on a page
    sort_type = models.TextField()
    item_type = models.TextField()

class CompBatch(models.Model):
    experiment = models.ForeignKey(CompExperiment)

class CompGroup(models.Model):
    batch = models.ForeignKey(CompBatch)
    vals = models.ManyToManyField(CompVal)

class CompAccess(models.Model):
    batch = models.ForeignKey(CompBatch)
    aid = models.CharField(max_length=128, null=True)
    hid = models.CharField(max_length=128, null=True)
    wid = models.CharField(max_length=128, null=True)
    preview = models.BooleanField()
    tstamp = models.DateTimeField(auto_now_add=True)

class CompRespMeta(models.Model):
    batch = models.ForeignKey(CompBatch)
    aid = models.CharField(max_length=128)
    hid = models.CharField(max_length=128)
    wid = models.CharField(max_length=128)
    accept_time = models.DateTimeField(null=False)
    submit_time = models.DateTimeField(null=False)

COMP_CHOICES = (
    ('gt', 'greater than'),
    ('eq', 'equal to'),
    ('lt', 'less than'),
)

class CompRespAns(models.Model):
    crm = models.ForeignKey(CompRespMeta)
    v1 = models.ForeignKey(CompVal, related_name="v1_set")
    v2 = models.ForeignKey(CompVal, related_name="v2_set")
    comp = models.CharField(max_length=2, choices=COMP_CHOICES)

class RateRespAns(models.Model):
    crm = models.ForeignKey(CompRespMeta)
    val = models.ForeignKey(CompVal)
    rating = models.IntegerField()

# Batch join logic
class BPExperiment(models.Model):
    run_name = models.TextField(unique=True)
    smart_interface = models.BooleanField()
    random = models.BooleanField()
    batch_size = models.IntegerField()

    def get_answers(self, workerid=None):
        if workerid:
            return BPRespAns.objects.filter(bprm__wid=workerid, bprm__batch__experiment=self)
        return BPRespAns.objects.filter(bprm__batch__experiment=self)

    def get_workers(self):
        workerids = set()
        for meta in BPRespMeta.objects.filter(batch__experiment=self):
            workerids.add(meta.wid)
        return list(workerids)


class BPPair(models.Model):
    left = models.IntegerField()
    right = models.IntegerField()

class BPBatch(models.Model):
    pairs = models.ManyToManyField(BPPair)
    experiment = models.ForeignKey(BPExperiment)

class BPAccess(models.Model):
    batch = models.ForeignKey(BPBatch)
    aid = models.CharField(max_length=128, null=True)
    hid = models.CharField(max_length=128, null=True)
    wid = models.CharField(max_length=128, null=True)
    preview = models.BooleanField()
    tstamp = models.DateTimeField(auto_now_add=True)

class BPRespMeta(models.Model):
    batch = models.ForeignKey(BPBatch)
    aid = models.CharField(max_length=128)
    hid = models.CharField(max_length=128)
    wid = models.CharField(max_length=128)
    accept_time = models.DateTimeField(null=False)
    submit_time = models.DateTimeField(null=False)

class BPRespAns(models.Model):
    bprm = models.ForeignKey(BPRespMeta)
    pair = models.ForeignKey(BPPair)
    same = models.BooleanField()

# Feature extraction/filter model objects
class FeatureVal(models.Model):
    name = models.TextField()
    order = models.IntegerField()

class Feature(models.Model):
    name = models.TextField()
    order = models.IntegerField()
    vals = models.ManyToManyField(FeatureVal)

class FeatureExperiment(models.Model):
    features = models.ManyToManyField(Feature)
    batch = models.BooleanField()
    run_name = models.TextField()

class FeatureCeleb(models.Model):
    cid = models.IntegerField()
    image_set = models.IntegerField()
    experiment = models.ForeignKey(FeatureExperiment)

class FeatureAccess(models.Model):
    celeb = models.ForeignKey(FeatureCeleb)
    featurenum = models.IntegerField()
    aid = models.CharField(max_length=128, null=True)
    hid = models.CharField(max_length=128, null=True)
    wid = models.CharField(max_length=128, null=True)
    preview = models.BooleanField()
    tstamp = models.DateTimeField(auto_now_add=True)

class FeatureRespMeta(models.Model):
    celeb = models.ForeignKey(FeatureCeleb)
    aid = models.CharField(max_length=128)
    hid = models.CharField(max_length=128)
    wid = models.CharField(max_length=128)
    accept_time = models.DateTimeField(null=False)
    submit_time = models.DateTimeField(null=False)

class FeatureRespAns(models.Model):
    fr = models.ForeignKey(FeatureRespMeta)
    feature = models.ForeignKey(Feature)
    val = models.ForeignKey(FeatureVal)

# Original join example models
class Pair(models.Model):
    left = models.IntegerField()
    right = models.IntegerField()
    run_name = models.TextField()
    # yes/no is legacy.  used to count the number of yes/no votes, but not any
    # longer.
    yes = models.IntegerField(default=0)
    no = models.IntegerField(default=0)
    
class PairResp(models.Model):
    pair = models.ForeignKey(Pair)
    aid = models.CharField(max_length=128)
    hid = models.CharField(max_length=128)
    wid = models.CharField(max_length=128)
    accept_time = models.DateTimeField(null=False)
    submit_time = models.DateTimeField(null=False)
    same = models.BooleanField()

class Access(models.Model):
    pair = models.ForeignKey(Pair)
    aid = models.CharField(max_length=128, null=True)
    hid = models.CharField(max_length=128, null=True)
    wid = models.CharField(max_length=128, null=True)
    preview = models.BooleanField()
    tstamp = models.DateTimeField(auto_now_add=True)
