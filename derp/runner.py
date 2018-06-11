from django.contrib.auth import get_user_model
from django.db import connection

from .models import Test, TestGroup

import traceback, sys, json
import datetime

from derp import config, t

class BaseRunner(object):
    def __init__(self,*args,**params):
        testgroup = params.pop("testgroup",None)
        self.params = params
        self.test, new = Test.objects.get_from_parameters(
            type=self.test_type,
            parameters=params,
        )
        if testgroup:
            self.test.testgroup = testgroup
            self.test.save()
    def run(self):
        start = datetime.datetime.now()
        start_queries = len(connection.queries)
        try:
            content = self.parse_content(self.execute())
        except Exception,e:
            exc_info = sys.exc_info()
            content = "TEST FAILED: %s"%e
            if config.STABLE or content == self.test.result:
                pass
            else:
                traceback.print_exc()
                exit()

        #! TODO Currently this is clearly not giving the actual result. Look into it.
        queries = 0 # len(connection.queries)-start_queries
        seconds = (datetime.datetime.now() - start).total_seconds()
        verified = self.test.verify(content)
        if verified and not config.UNSTAGED_HASH:
            self.test.record_run(seconds,queries)
    def parse_content(self,content):
        content = content.replace(".0,",",").replace(".0\n","\n")
        try:
            j = json.loads(content)
        except ValueError:
            return content
        else:
            j = config._process_json(j) # custom json post-processing
            return json.dumps(j,sort_keys=True,indent=4)

class URLRunner(BaseRunner):
    test_type = 'url'
    def __init__(self,url,*args,**params):
        self.url = url
        params['url'] = url
        super(URLRunner,self).__init__(*args,**params)
        self.user = None
        self.url_params = {}
        if 'email' in params:
            self.user = get_user_model().objects.get(email=params['email'])
            self.url_params = config.PREP_VARIABLES(email=params['email'])
    def run(self):
        if 'email' in self.params:
            t.login(self.params['email'])
        super(URLRunner,self).run()
    def execute(self):
        #print self.url.format(**self.url_params)
        response = t.client.get(self.url.format(**self.url_params))
        content = response.content
        if response.status_code == 404:
            content = "404'd!"
        if self.url in config.force_sort:
            lines = content.split("\n")
            content = "\n".join(lines[0:1]+sorted(lines[1:]))
        return content
