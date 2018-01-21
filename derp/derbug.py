from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection,connections
from django.test import Client
from django.utils import timezone

import datetime, os, json, difflib, subprocess, traceback, sys
from collections import defaultdict
from derp import config
from derp.models import Test, TestRun

class Track():
    def __init__(self,**kwargs):
        if "run_derp" in sys.argv:
            settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        self.git_hash = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE).communicate()[0]
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
        now = datetime.datetime.now()
        count = len(connection.queries) - self.queries_count
        print self.dt(self.start),'\t',self.dt(self.last),'\t',count,'q\t@',s
        self.queries_count = len(connection.queries)
        self.last = datetime.datetime.now()
    def __del__(self):
        for group,files in self.groups.items():
            f = open(group,"w")
            f.write("\n".join(files))
            f.write("\n") # need an extra end of line for reasons thus unknown
            f.close()
        if self.groups:
            print "wrote "," ".join(self.groups.keys())

    def dt(self,t):
        ms = int(1000*(datetime.datetime.now()-t).total_seconds())
        if ms < 1000:
            return "%sms"%ms
        if ms < 10000:
            return "%.2fs"%(ms/1000.)
        return "%.1fs"%(ms/1000.)
    def clear(self,s=None):
        self.logged_in = None
        if s:
            print s
        self.start = self.last = datetime.datetime.now()
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

    def parse_content(self,content,parse_json=True):
        content = content.replace(".0,",",").replace(".0\n","\n")
        if not parse_json:
            return content
        try:
            j = json.loads(content)
        except ValueError:
            pass
        else:
            # The current code has some messed up sorting
            if 'season_points_breakdown' in j:
                j['season_points_breakdown'] = sorted(j['season_points_breakdown'])
            if 'results' in j:
                j['results'] = sorted(j['results'],key=lambda d:(d.get("points",None),d.get("last_name",None)))
                for result in j['results']:
                    if result.get("team_ids",None):
                        result['team_ids'] = sorted(result['team_ids'])
            content = json.dumps(j,sort_keys=True,indent=4)
        return content

    def verify_email_message(self,email,name,params):
        test,new = Test.objects.get_from_parameters(
            type='email',
            name=name,
            parameters=params,
        )
        if new:
            print "Test created: %s"%test
        content = "SUBJECT:{}\nTO:{}nFROM:{}\n\n--==BODY==--{}\n"
        content = content.format(email.subject,email.to,email.from_email,email.body)
        for text,mime_type in email.alternatives:
            content += "\n\n--=={}==--\n{}".format(mime_type,text)
        test.verify(content)
    def verify_url(self,url,params):
        test,new = Test.objects.get_from_parameters(
            type='url',
            name=params['url'],
            parameters=params,
        )
        if new:
            print "Test created: %s"%test
        url = url.format(**params)
        start = datetime.datetime.now()
        start_queries = len(connection.queries)
        try:
            content = self.parse_content(self.curl(url))
        except ImportError,e:
            content = "TEST FAILED\n\n%s"%url
            if config.STABLE or content == test.result:
                pass
            else:
                raise Exception(e)
        queries = len(connection.queries)-start_queries
        seconds = (datetime.datetime.now() - start).total_seconds()
        if test.verify(content):
            test.record_run(seconds,queries,self.git_hash)

    def curl(self,url,fpath=None):
        #cProfile.runctx("response = client.get(url)",None,locals())
        response = self.client.get(url)
        return response.content

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