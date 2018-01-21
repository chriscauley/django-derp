from django.db import models

from derp.fields import JSONField
from derp import config

import hashlib, json

class TestManager(models.Manager):
    def get_from_parameters(self,*args,**kwargs):
        parameters = kwargs.pop("parameters")
        kwargs['parameters_hash'] = hashlib.md5(json.dumps(parameters,sort_keys=True)).hexdigest()
        obj,new = super(TestManager,self).get_or_create(*args,**kwargs)
        obj.parameters = parameters
        obj.save()
        return obj,new

class Test(models.Model):
    class Meta:
        app_label = "derp"
    objects = TestManager()
    TEST_CHOICES = [
        ('url','url'),
    ]
    type = models.CharField(max_length=16,choices=TEST_CHOICES)
    name = models.CharField(max_length=128,help_text="Verbose Test being called (eg. a url, task, or function")
    parameters = JSONField(default=dict)
    parameters_hash = models.CharField(max_length=32,default="arst")
    result = models.TextField(default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def save(self,*args,**kwargs):
        self.parameters_hash = hashlib.md5(json.dumps(self.parameters,sort_keys=True)).hexdigest()
        super(Test,self).save(*args,**kwargs)
    def verify(self,content):
        from derp import t
        if config.STABLE:
            self.result = content
            self.save()
            t("wrote %s"%self)
            return True
        elif not self.result:
            raise ValueError("Stable result not recorded for %s"%self)
        elif self.result == content:
            t("PASS: %s"%self)
            return True
        else:
            # maybe this should be on t?
            import os, difflib
            name = str(self).replace(" ","/").replace("#","")
            diff_dir = "/".join(name.split("/")[:-1])
            fname = name.split("/")[-1]
            diff_dir = t.mkdir(diff_dir,prefix=".diff")
            diff_path = os.path.join(diff_dir,"%s.diff"%fname)
            d = "\n".join(difflib.unified_diff(self.result.split("\n"),content.split("\n")))
            t.write_file(diff_path,d,group="DIFF")
            t("CHANGED: %s %s"%(self.id,self))
    def record_run(self,seconds,queries,git_hash):
        run = TestRun.objects.create(
            test=self,
            commit_hash=git_hash,
            queries=queries,
            milliseconds=int(1000*seconds)
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
        if self.name.startswith("/") and 'email' in self.parameters: #probably a url
            return "%s: %s %s"%(self.type,self.get_short_url(),self.get_short_email())
        return self.name


class TestRun(models.Model):
    class Meta:
        app_label = "derp"
    test = models.ForeignKey(Test)
    commit_hash = models.CharField(max_length=32)
    queries = models.IntegerField()
    milliseconds = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
