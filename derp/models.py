from django.core.urlresolvers import resolve, Resolver404
from django.db import models

from derp.fields import JSONField
from derp import config

import hashlib, json, subprocess

class JsonModel(models.Model):
    class Meta:
        abstract=True
    json_fields = []
    @property
    def as_json(self):
        return {k:getattr(self,k) for k in self.json_fields}

class CommitManager(models.Manager):
    def refresh(self):
        self.all().update(parent=None)
        _cmd = 'git log --pretty=format:%H'
        hashes = subprocess.Popen(_cmd.split(" "),stdout=subprocess.PIPE).communicate()[0].split("\n")
        parent = None
        for _hash in hashes:
            commit, new = self.get_or_create(id=_hash,defaults={'order':0})
            commit.parent = parent
            commit.order = parent.order + 1
            commit.save()
            parent = commit

class Commit(JsonModel):
    class Meta:
        ordering = ("-order",)
    __unicode__ = lambda self: self.id
    json_fields = ['parent_id','order','id']
    parent = models.ForeignKey('self', related_name='children', blank=True, null=True)
    order = models.IntegerField(default=0)
    id = models.CharField(max_length=32,primary_key=True)
    objects = CommitManager()
    def save(self,*args,**kwargs):
        if self.parent_id:
            self.order = self.parent.order + 1
        super(Commit,self).save(*args,**kwargs)

class TestManager(models.Manager):
    def get_from_parameters(self,*args,**kwargs):
        parameters = kwargs.pop("parameters")
        kwargs['parameters_hash'] = hashlib.md5(json.dumps(parameters,sort_keys=True)).hexdigest()
        obj,new = super(TestManager,self).get_or_create(*args,**kwargs)
        obj.parameters = parameters
        obj.save()
        return obj,new

class Test(JsonModel):
    json_fields = ['id','type','parameters','url_name']
    objects = TestManager()
    TEST_CHOICES = [
        ('url','URL'),
        ('task','TASK'),
    ]
    type = models.CharField(max_length=16,choices=TEST_CHOICES)
    parameters = JSONField(default=dict)
    parameters_hash = models.CharField(max_length=32,default="arst")
    result = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    @property
    def url_name(self):
        if not 'url' in self.parameters:
            return
        url_params = {'client_id': 1,'team_id': 1}
        url_parts = self.parameters['url'].format(**url_params)
        url = url_parts[0]
        qs = ""
        try:
            return resolve(url).view_name
        except Resolver404:
            return url
    def save(self,*args,**kwargs):
        self.parameters_hash = hashlib.md5(json.dumps(self.parameters,sort_keys=True)).hexdigest()
        super(Test,self).save(*args,**kwargs)
    def verify(self,content):
        from derp import t
        old_result = self.result or ""
        success = False
        if config.STABLE:
            verb = "SAME" if self.result == content else ("UPDATED %s>%s"%(len(self.result),len(content)))
            if not old_result:
                verb = "WROTE"
            self.result = content
            self.save()
            t("%s %s"%(verb,self))
            success = True
        elif not self.result:
            raise ValueError("Stable result not recorded for %s"%self)
        elif self.result == content:
            t("PASS: %s"%self)
            success = True
        if old_result and old_result != content:
            # maybe this should be on t?
            import os, difflib
            name = str(self).replace(" ","/").replace("#","")
            diff_dir = "/".join(name.split("/")[:-1])
            fname = name.split("/")[-1]
            diff_dir = t.mkdir(diff_dir,prefix=".diff")
            diff_path = os.path.join(diff_dir,"%s.diff"%fname)
            d = "\n".join(difflib.unified_diff(old_result.split("\n"),content.split("\n")))
            t.write_file(diff_path,d,group="DIFF")
            t("CHANGED: %s %s"%(self.id,self))
        return success
    def record_run(self,seconds,queries,status='pass'):
        Commit.objects.get_or_create(id=config.COMMIT_HASH)
        run = TestRun.objects.create(
            test=self,
            commit_id=config.COMMIT_HASH,
            queries=queries,
            milliseconds=int(1000*seconds),
            status=status
        )
    def get_short_url(self):
        url = self.name.split("?")[0]
        short_url = "/".join([s[0] for s in url.split("/") if s])
        qs = self.name.split("?")[-1] if "?" in self.name else ""
        short_qs = qs
        if "&" in qs:
            short_qs = "?...&"+qs.split("&")[-1]
        elif qs:
            short_qs = "?"+short_qs
        return "/%s%s"%(short_url,short_qs)
    def get_short_email(self):
        username,domain = self.parameters['email'].split("@")
        return "%s@%s"%(username[0],domain)
    def __unicode__(self):
        out = self.type.upper()+": "
        items = [self.parameters.get(key,None) for key in ['url','task_name','email']]
        items = " ".join([i for i in items if i])
        return self.type.upper()+": " + items

STATUS_CHOICES = [
    ('pass','pass'),
    ('fail','fail'),
    ('unknown','unknown'),
]

class TestStatus(JsonModel):
    __unicode__ = lambda self: "Test #%s @%s: %s"%(self.test_id,self.commit,self.status) 
    json_fields = ['id','test_id','commit_id','status','average_ms','run_count']
    test = models.ForeignKey(Test)
    commit = models.ForeignKey('derp.Commit')
    status = models.CharField(max_length=16,choices=STATUS_CHOICES,default='unknown')
    average_ms = models.IntegerField(default=0)
    run_count = models.IntegerField(default=0)
    def save(self,*args,**kwargs):
        times = TestRun.objects.filter(test_id=self.test_id,commit_id=self.commit_id,status='pass')
        times = list(times.values_list('milliseconds',flat=True))
        self.average_ms = sum(times)/len(times) if times else 0
        self.run_count = len(times)
        super(TestStatus,self).save()

class TestRun(JsonModel):
    __unicode__ = lambda self: "%s"%self.test_id
    test = models.ForeignKey(Test)
    commit = models.ForeignKey('derp.Commit',null=True,blank=True)
    queries = models.IntegerField()
    milliseconds = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16,choices=STATUS_CHOICES,default='unknown')
    def save(self,*args,**kwargs):
        if not self.id:
            teststatus,new = TestStatus.objects.get_or_create(test=self.test,commit=self.commit)
            if teststatus.status != self.status:
                teststatus.status = self.status
                teststatus.save()
        super(TestRun,self).save(*args,**kwargs)