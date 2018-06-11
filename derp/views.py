from django.http import JsonResponse
from django.template.response import TemplateResponse

from derp import config
from derp.models import Test, TestStatus, Commit, TestGroup

from collections import defaultdict
import subprocess, hashlib

TARGETS = { k: v for k,v in config.TARGETS.items() }
COMMANDS = { k: v for k,v in config.COMMANDS.items() if not k.startswith("_") }
HASH_DICT = {}
_cmd = 'git log --pretty=format:%H'

def hash(request):
    return JsonResponse({
        'git': config.COMMIT_HASH,
        'unstaged': config.UNSTAGED_HASH or None
    })

def result_json(request):
    commit_list = [c.as_json for c in Commit.objects.filter(name__isnull=False)]
    commit_ids = [c['id'] for c in commit_list]
    tests = [t for t in Test.objects.all() if t.parameters.get("email",None) in TARGETS['_all']]
    return JsonResponse({
        'status_list': [ts.as_json for ts in TestStatus.objects.filter(test__in=tests,commit_id__in=commit_ids)],
        'tests': {t.id: t.as_json for t in tests},
        'commit_list': commit_list,
        'commands': COMMANDS,
        'targets': TARGETS,
        'group_list': [g.as_json for g in TestGroup.objects.all()]
    })

def commits_json(request):
    commit_list = [c.as_json for c in Commit.objects.filter(name__isnull=False)]

def result(request):
    return TemplateResponse(request,'derp/index.html',{})