import sys,os,base64,time,math,hashlib,traceback
from datetime import datetime, timedelta
from qurkexp.hitlayer import settings
from django.db import models
from django.db import transaction

from boto.mturk import connection, question, price, qualification




class HIT(models.Model):
    hid = models.CharField(max_length=128)
    autoapprove = models.BooleanField(default=True)
    cbname = models.CharField(max_length=128, null=True)
    done = models.BooleanField(default=False)
    start_tstamp = models.DateTimeField(auto_now_add=True)
    url = models.TextField(null=True)

    def _cbargs(self):
        return [arg.val for arg in self.cbarg_set.order_by('idx')]
    cbargs = property(_cbargs)

    def kill(self):
        if self.done: return
        try:
            HitLayer.get_instance().kill_job(self.hid)
            self.done = True
            self.save()
        except:
            pass

class CBArg(models.Model):
    hit = models.ForeignKey(HIT)
    idx = models.IntegerField()
    val = models.CharField(max_length=128)

class HitLayer(object):
    """
    continuously keeps HITs on MTurk until they're completed
    if a HIT expires, it extends the lifetime
    approves all results seen
    """
    myinstance = None
    
    def __init__(self):
        self.conn = self.get_conn()
        self.generators = dict()
        HitLayer.myinstance = self

    @staticmethod
    def get_instance():
        if HitLayer.myinstance == None:
            HitLayer.myinstance = HitLayer()
        return HitLayer.myinstance

    def register_cb_generator(self, gname, generator):
        """
        The generator creates and returns a callback function that takes the
        hitid and answers (list of dictionaries) as input

        The generator itself can take a number of arguments that help setup
        the context for the callback
        
        The generator is of the format:

        def generator(arg1, arg2,...):
            # setup code, based on arg1, arg2...
            
            def cb(hitid, answers):
                pass
            return cb
        """
        if gname in self.generators:
            print "Warning: overwriting existing generator with name: ", gname
        self.generators[gname] = generator
    
    def get_conn(self,sandbox=settings.SANDBOX):
        """
        returns a connection.
        requires that settings defines the following variables:

        settings.SANDBOX:    True|False
        settings.aws_id:     your aws id
        settings.aws_secret: your aws secret key
        """
        if sandbox:
            host="mechanicalturk.sandbox.amazonaws.com"
        else:
            host="mechanicalturk.amazonaws.com"
        return connection.MTurkConnection(
            aws_access_key_id=settings.aws_id,
            aws_secret_access_key=settings.aws_secret,
            host=host)
    
    def persist_hit(self, hitid, autoapprove, callback, url):
        """
        Save HIT information in database
        """
        hit = HIT(hid = hitid, autoapprove=autoapprove, url=url)
        hit.save()
        if callback:
            hit.cbname = callback[0]
            for i, arg in enumerate(callback[1]):
                cbarg = CBArg(hit=hit, idx=i, val=str(arg))
                cbarg.save()
            hit.save()

        
    def create_job(self, url, callback, nassignments = 1, title='', desc='', timeout=60*5, price=0.02, autoapprove=True):
        if not url: return None
        c = self.conn
        balance = c.get_account_balance()
        if balance < price:
            return None
        if balance < price * 10:
            print "Warning: you are running low on funds: ", balance

        price = connection.MTurkConnection.get_price_as_price(price)
        q = question.ExternalQuestion('%s%s' % (settings.URLROOT, url), 750)
        print url, title, price, timeout
        
        rs = c.create_hit(hit_type=None,
                          question=q,
                          lifetime=timedelta(5),
                          max_assignments=nassignments,
                          title=title,
                          duration=timedelta(seconds=timeout),
                          approval_delay=60*60,
                          description=desc,
                          reward = price)
        hitids = [r.HITId for r in rs if hasattr(r, 'HITId')]
        if len(hitids) == 0: return None
        hitid = hitids[0]

        self.persist_hit(hitid, autoapprove, callback, url)
        
        return hitid

    def kill_job(self, hitid, msg='Thank you for doing this HIT'):
        """
        Approve finished assignments, then expire, disable, and dispose the HIT
        """
        try:
            c = self.conn
            print 'kill_job ', hitid
            rs = c.get_assignments(hitid, status='Submitted')
            for ass in rs:
                c.approve_assignment(ass.AssignmentId, msg)
            killed = False
            try:
                c.expire_hit(hitid)
                killed = True            
            except Exception as ee:
                pass
            try:
                c.disable_hit(hitid)
                killed = True
            except Exception as ee:
                pass
            try:
                c.dispose_hit(hitid)
                killed = True
            except Exception as ee:
                pass
            print 'killed?', killed            
        except Exception as e:
            print e

    @transaction.commit_manually
    def check_hits(self):
        """
        Iterates through all the HITs in the database where done=False
        For each HIT that is in the Reviewable state (all assignments completed)
         1) extracts all assignment results
         2) if autoapprove is true, approved the assignments and disposes the HIT
         3) executes the HIT's callback function
         4) sets the HIT database object to done=True
        """
        try:
            for hitobj in HIT.objects.filter(done=False):
                try:
                    self.check_hit(hitobj)
                except Exception as e:
                    print 'check_hits: problem processing', hitobj.hid
                    print e
                    print traceback.print_exc()
                    transaction.rollback()
                else:
                    transaction.commit()
        finally:
            # django transactions are fucked.
            # this is the dumbest piece of code i've ever written.
            transaction.rollback()

    def check_hit(self, hitobj):
        hitid = hitobj.hid
        mthit = self.get_mthit(hitid)
        if not mthit:
            print 'check_hits: didnt find hit for ', hitid
            return 
        status = mthit.HITStatus
        print 'check_hits', hitid, status, hitobj.url
        if status == 'Reviewable':

            
            if self.process_reviewable(hitid, hitobj.autoapprove):
                hitobj.done = True
                hitobj.save()
            else:
                print 'check_hits: problem processing', hitid
            # the previous block should be atomic                
            print 'approved', hitobj.hid
        elif status in ['Assignable','Disposed','Unassignable','Reviewing']:
            pass
        

    def process_reviewable(self, hitid, autoapprove):
        allans = self.get_hit_answers(hitid)
                
        if autoapprove:
            for ans in allans:
                if ans['purk_status'] == 'Submitted':
                    aid = ans['purk_aid']
                    print "approving assignment ", aid, ans['purk_status']
                    self.approve_assignment(aid)

        cb = self.get_callback(hitid)
        cb(hitid, allans)
        # should remember that callback was executed, so we
        # don't execute it again!

        self.conn.dispose_hit(hitid)
        print 'hit disposed', hitid

        return True

        
        
        

    def get_hit_answers(self, hitid):
        """
        retrieves all the answers for all assignments for the HIT
        returns an array of dictionaries.
        Each dictionary has several purk-related entries:
          purk_aid      assignment id
          purk_wid      worker id
          purk_atime    accept time (datetime object)
          purk_stime    submit time (datetime object)
          purk_length   submit time - accept time (timedelta object)
        """
        allans =[]
        for a in self.get_assignments(hitid):
            aid = a.AssignmentId
            wid = a.WorkerId
            accepttime = datetime.strptime(a.AcceptTime, '%Y-%m-%dT%H:%M:%SZ')
            submittime = datetime.strptime(a.SubmitTime, '%Y-%m-%dT%H:%M:%SZ')
            
            d = {}
            d['purk_status'] = a.AssignmentStatus
            d['purk_aid'] = aid
            d['purk_wid'] = wid
            d['purk_atime'] = accepttime
            d['purk_stime'] = submittime
            d['purk_length'] = submittime - accepttime
            for answers in a.answers:
                for answer in answers:
                    d.update((k,v) for k,v in answer.fields)
            allans.append(d)
        return allans

    def get_mthit(self, hitid):
        """
        Return the mechanical turk (boto) HIT object, or None if HIT is not found
        """
        try:
            return self.conn.get_hit(hitid)[0]
        except:
            return None

    def get_hit(self, hitid):
        """
        Return the HIT database object
        """
        try:
            return HIT.objects.get(hid=hitid)
        except:
            return None

    def get_assignments(self, hitid):
        """
        Return the boto assignment objects from mechanical turk
        """
        return self.conn.get_assignments(hitid)

    def approve_assignment(self, aid):
        self.conn.approve_assignment(aid, "Thank you!")

    def reject_assignment(self, aid, msg=""):
        self.conn.reject_assignment(aid, msg)


    def get_callback(self, hitid):
        def dummycb(hitid, answers):
            pass
        
        hit = self.get_hit(hitid)
        try:
            # if not hit or not hit.cbname:
            #     return None
            # if hit.cbname not in self.generators:
            #     return None
            ret = self.generators[hit.cbname](*hit.cbargs)
            if ret:
                return ret
            return dummycb
        except Exception as e:
            print e
            print traceback.print_exc()
            return dummycb

