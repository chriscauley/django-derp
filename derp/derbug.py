from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection,connections
from django.test import Client
from django.utils import timezone

import datetime, os, json, difflib, subprocess, traceback
from collections import defaultdict
from derp import config

class Track():
    def __init__(self,**kwargs):
        self.git_hash = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE).communicate()[0]
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
            if 'results' in j:
                j['results'] = sorted(j['results'],key=lambda d:(d.get("points",None),d.get("last_name",None)))
                for result in j['results']:
                    if result.get("team_ids",None):
                        result['team_ids'] = sorted(result['team_ids'])
            content = json.dumps(j,sort_keys=True,indent=4)
        return content

    def verify(self,content,*args):
        content = self.parse_content(content)
        fpath = os.path.join(*args)
        _parts = fpath.split("/")
        write_dir = self.mkdir("/".join(_parts[:-1]))
        fname = _parts[-1]
        write_path = os.path.join(write_dir,fname)
        path_display = write_path.replace(self.prefix,"")
        path_display = path_display if len(path_display) < 55 else "..."+path_display[-45:]
        if config.STABLE:
            self.write_file(write_path,content,group="RESULTS")
            self("wrote %s"%path_display)
            return
        if not os.path.exists(write_path):
            raise ValueError("No file to compare against: %s"%write_path)
        with open(write_path,'r') as f:
            old = self.parse_content(f.read())
            if content == old:
                self("PASS: %s"%path_display)
                self.groups['PASS'].append(write_path)
            else:
                self("CHANGED: %s"%path_display)
                self.groups['CHANGED'].append(write_path)
                d = "\n".join(difflib.unified_diff(old.split("\n"),content.split("\n")))
                diff_path = os.path.join(self.mkdir(".diff"),"%s.diff"%fname)
                self.write_file(diff_path,d,group="DIFF")

    def verify_url(self,url,email=None,password=None):
        if email:
            self.login(email,password)
        start = datetime.datetime.now()
        start_queries = len(connection.queries)
        content = self.curl(url)
        end_queries = len(connection.queries)
        seconds = (datetime.datetime.now() - start).total_seconds()
        self.record_result(url,email,seconds,end_queries-start_queries)
        self.verify(content,url,email)

    def curl(self,url,fpath=None):
        #cProfile.runctx("response = client.get(url)",None,locals())
        response = self.client.get(url)
        fpath = fpath or url.strip("/")
        return response.content

    def write_sql(self,s,content,comments=[]):
        fpath = "derp/.queries/%s.sql"%s
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

    def record_result(self,url,email,seconds,queries):
        fpath = ".dev/.__results.cache"
        with open(fpath,"r+") as f:
            results = json.loads(f.read() or "[]")
            results.append(dict(
                STABLE=config.STABLE,
                url=url,
                email=email,
                seconds=seconds,
                queries=queries,
                created=str(timezone.now()),
                git_hash=self.git_hash,
            ))
            f.seek(0)
            f.write(json.dumps(results))
            f.truncate()
t = Track()