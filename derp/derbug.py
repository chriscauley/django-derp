from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection, connections
from django.test import Client
from django.utils import timezone

import os, json, difflib, subprocess, traceback, sys, freezegun
from collections import defaultdict
from derp import config

real_datetime = freezegun.api.real_datetime

class Track():
    def __init__(self,**kwargs):
        if "run_derp" in sys.argv:
            settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        STABLE = config.STABLE
        self.groups = defaultdict(list)
        self.cursor = connections['default'].cursor()
        self.clear()
        self.client = Client()
        self.prefix = kwargs.get('prefix',".__results")
    def __call__(self,s=""):
        if not s:
            _f,line_no,func,_t = traceback.extract_stack()[-2]
            parts = _f.split("/")
            s = "%s: %s@%s"%(parts[-1],func,line_no)
            s = ">"*(len(parts)-1) + " " + s
        now = real_datetime.now()
        count = len(connection.queries) - self.queries_count
        print self.dt(self.start),'\t',self.dt(self.last),'\t',count,'q\t@',s
        self.queries_count = len(connection.queries)
        self.last = real_datetime.now()
    def __del__(self):
        for group,files in self.groups.items():
            f = open(group,"w")
            f.write("\n".join(files))
            f.write("\n") # need an extra end of line for reasons thus unknown
            f.close()
        if self.groups:
            print "wrote "," ".join(self.groups.keys())

    def dt(self,t):
        ms = int(1000*(real_datetime.now()-t).total_seconds())
        if ms < 1000:
            return "%sms"%ms
        if ms < 10000:
            return "%.2fs"%(ms/1000.)
        return "%.1fs"%(ms/1000.)
    def clear(self,s=None):
        self.logged_in = None
        if s:
            print s
        self.start = self.last = real_datetime.now()
        self.queries_count = 0

    def login(self,email,password=None,force=True):
        if self.logged_in == email:
            return
        password = password or "password1"
        u = get_user_model().objects.get(email=email)
        if not u.check_password(password) and force:
            u.set_password(password)
            u.save()
        self.client.login(username=email,password=password)
        u.logged_in = email
    def mkdir(self,path,prefix=None):
        prefix = prefix or self.prefix
        p = ""
        path = path.strip('/')
        if not path.startswith(prefix):
            path = os.path.join(prefix,path)
        for d in path.split("/"):
            p = os.path.join(p,d)
            if not(os.path.exists(p)):
                os.mkdir(p)
        return p

    def parse_email_message(self,email):
        content = "SUBJECT:{}\nTO:{}\nFROM:{}\n\n--==BODY==--{}\n"
        content = content.format(email.subject,email.to,email.from_email,email.body)
        for text,mime_type in email.alternatives:
            content += "\n\n--=={}==--\n{}".format(mime_type,text)
        return content

    def write_sql(self,s,content,comments=[]):
        fpath = ".dev/derp/.queries/%s.sql"%s
        if os.path.exists(fpath):
            return
        head = ""
        for c in comments:
            head = head + "#%s\n"%c
        self.write_file(fpath,head+content)
        arst
    def write_file(self,path,content,group=None):
        with open(path,'w') as f:
            f.write(content)
        group and self.groups[group].append(path)
t = Track()