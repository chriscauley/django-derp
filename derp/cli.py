import os,django;os.environ['DJANGO_SETTINGS_MODULE'] = 'settings';django.setup()

from django.core.urlresolvers import reverse

from derbug import t

import json

results = {}
RESULTS_PATH = ".__results/.cache.json"
if os.path.exists(RESULTS_PATH):
    with open(RESULTS_PATH,'r') as f:
        results = json.loads(f.read())

members = [
    'rdemuth@frontlineselling.com',
    'Elizabeth.hatchel@fiserv.com',
    'paul.stabile@fiserv.com',
    'paul.arena@experian.com',
    'anthony.peters@protiviti.com',
    "jenny.hollingworth@protiviti.com"
]
urls = [
    #reverse('api:admin-report-engagement',args=['shares','2014-01-13','2017-11-13']),
    #'/api/cards/pending/', '/api/cards/completed/', '/api/cards/dismissed/',
    '/api/cards/totals/',
    #'/api/optimizations/totals/',
    #'/api/optimizations/completed/',
    #'/api/timeline/?cutoff_date=2017-11-03T02:50:11',
    #'/api/articles/new/','/api/articles/shared/','/api/articles/dismissed/',
    #'/api/users/leaderboard',
]
for email in members:
    t.clear(email)
    for url in urls:
        t.verify_url(url,email)

# This url is the 8 second one
# "/api/users/manager/deals"