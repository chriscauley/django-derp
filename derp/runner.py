from django.contrib.auth import get_user_model
from django.db import connection

from .models import Test

import traceback, sys, json
import datetime

from derp import config, t

class BaseRunner(object):
    def __init__(self,*args,**params):
        self.params = params
        self.test, new = Test.objects.get_from_parameters(
            type=self.test_type,
            name=self.get_name(),
            parameters=params,
        )
    def run(self):
        start = datetime.datetime.now()
        start_queries = len(connection.queries)
        try:
            content = self.parse_content(self.execute())
        except ImportError,e:
            exc_info = sys.exc_info()
            content = "TEST FAILED: %s"%e
            if config.STABLE or content == self.test.result:
                pass
            else:
                traceback.print_exc()
                raise Exception(e)

        #! TODO Currently this is clearly not giving the actual result. Look into it.
        queries = 0 # len(connection.queries)-start_queries
        seconds = (datetime.datetime.now() - start).total_seconds()
        verified = self.test.verify(content)
        if verified:
            if config.UNSTAGED_HASH:
                print "Cannot save due to unstaged commits"
            else:
                self.test.record_run(seconds,queries)
    def parse_content(self,content):
        content = content.replace(".0,",",").replace(".0\n","\n")
        try:
            j = json.loads(content)
        except ValueError:
            pass
        else:
            # The current code has some messed up sorting
            if 'season_points_breakdown' in j:
                j['season_points_breakdown'] = sorted(j['season_points_breakdown'])
            if 'results' in j:
                j['results'] = sorted(j['results'],key=lambda d:(-d.get("points",0),d.get("last_name",None)))
                for result in j['results']:
                    if result.get("team_ids",None):
                        result['team_ids'] = sorted(result['team_ids'])
            content = json.dumps(j,sort_keys=True,indent=4)
        return content

class URLRunner(BaseRunner):
    test_type = 'url'
    def __init__(self,url,*args,**params):
        self.url = url
        super(URLRunner,self).__init__(*args,**params)
        self.user = None
        self.url_params = {}
        if 'email' in params:
            self.user = get_user_model().objects.get(email=params['email'])
            self.url_params = { 'client_id': self.user.client_id, 'team_id': self.user.primary_team_id }
    def run(self):
        if 'email' in self.params:
            t.login(self.params['email'])
        super(URLRunner,self).run()
    def execute(self):
        content = t.client.get(self.url.format(**self.url_params)).content
        return content
    def get_name(self):
        return "%s %s"%(self.url,self.params.get("email",None))
