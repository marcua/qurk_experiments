from django.db import models

# The kind of item we are estimating properties of
class Kind(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name

# Items whose properties we are estimating
class Item(models.Model):
    kind = models.ForeignKey(Kind, related_name="items")
    ident = models.TextField() # a compact unique identifier
    data = models.TextField() # app-specific information

    class Meta:
        unique_together = ("kind", "ident")

    def __getitem__(self, prop):
        for ann in self.annotations.filter(prop=prop):
            return ann.val
        return super(Item, self).__getitem__(prop)

    def __str__(self):
        return "%s: %s (%d)" % (self.kind, self.ident, self.id)

# An item property annotation
class Annotation(models.Model):
    item = models.ForeignKey(Item, related_name="annotations")
    prop = models.TextField() # property name
    val = models.TextField() # property value
    class Meta:
        unique_together = ("item", "prop")

# An experiment to estimate some property of a collection of items
class EstExp(models.Model):
    name = models.TextField(unique=True)
    kind = models.ForeignKey(Kind, related_name="exps")
    prop = models.TextField() # property we're estimating

# Maps an experiment to all the Items in that experiment.
# Not a ManyToMany relationship so that an item can appear in an 
# experiment more than once.
class ExpItem(models.Model):
    exp = models.ForeignKey(EstExp, related_name="item_ptrs")
    item = models.ForeignKey(Item, related_name="exp_ptrs")

# A run on MTurk of an estimation experiment.  You set a batch size
# and a display style so that we can test various modes of estimating
# different samples.
class ExpRun(models.Model):
    exp = models.ForeignKey(EstExp, related_name="runs")
    name = models.TextField(unique=True)
    batch_size = models.IntegerField()
    num_batches = models.IntegerField()
    display_style = models.TextField()
    assignments = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        retval = "Experiment '%s', run '%s', batch size %d, display style %s"
        retval = retval % (self.exp.name, self.name, self.batch_size, self.display_style)
        return retval

# The values of the experiment properties to estimate.  A single
# worker can estimate multiple values at once.  For example, not only
# estimate how many blue squares, but also how many pink ones.
class RunVal(models.Model):
    run = models.ForeignKey(ExpRun, related_name="vals")
    val = models.TextField()

# A single batch of items that is displayed to a worker at once
class RunBatch(models.Model):
    run = models.ForeignKey(ExpRun, related_name="batches")
    items_ptrs = models.ManyToManyField(ExpItem, related_name="batches")

# The metadata for the response of a single worker
class ValRespMeta(models.Model):
    batch = models.ForeignKey(RunBatch)
    aid = models.CharField(max_length=128)
    hid = models.CharField(max_length=128)
    wid = models.CharField(max_length=128)
    accept_time = models.DateTimeField(null=False)
    submit_time = models.DateTimeField(null=False)
    seconds_spent = models.FloatField(default=-1)
    screen_height = models.IntegerField(default=-1)
    screen_width = models.IntegerField(default=-1)

# A single worker's estimation of a particular property value fraction
class ValRespAns(models.Model):
    vrm = models.ForeignKey(ValRespMeta)
    val = models.TextField()
    count = models.IntegerField()

# A single worker's label for an item's value
class ValRespValue(models.Model):
    vrm = models.ForeignKey(ValRespMeta)
    item = models.ForeignKey(ExpItem)
    val = models.TextField()
