from django.http import JsonResponse
from django.template.response import TemplateResponse

from derp import config
from derp.models import Test, TestStatus, Commit

from collections import defaultdict
import subprocess, hashlib

TARGETS = { k: v for k,v in config.TARGETS.items() if not k.startswith("_") }
COMMANDS = { k: v for k,v in config.COMMANDS.items() if not k.startswith("_") }
HASH_DICT = {}
_cmd = 'git log --pretty=format:%H'


def hash(request):
    return JsonResponse({
        'git': config.COMMIT_HASH,
        'unstaged': config.UNSTAGED_HASH or None
    })

def result_json(request):
    hashes = {h[1]:h[0] for h in config.HASH_NAMES}
    commit_list = [c.as_json for c in Commit.objects.filter(id__in=hashes)]
    [c.update(name=hashes[c['id']]) for c in commit_list]
    active_group =  COMMANDS[request.GET.get('group','leaderboard')]
    tests = [t for t in Test.objects.all() if t.parameters.get("url","") in active_group]
    return JsonResponse({
        'status_list': [ts.as_json for ts in TestStatus.objects.filter(test__in=tests)],
        'tests': {t.id: t.as_json for t in tests},
        'commit_list': commit_list,
        'commands': COMMANDS,
        'targets': TARGETS,
    })

def groups_json(request):
    hashes = {h[1]:h[0] for h in config.HASH_NAMES}
    commit_list = [c.as_json for c in Commit.objects.filter(id__in=hashes)]
    [c.update(name=hashes[c['id']]) for c in commit_list]
    groups = [{'name': g, 'commands': c} for g,c in config.COMMANDS.items() if not g.startswith("_")]
    return JsonResponse({
        'groups': groups
    })

def result(request):
    return TemplateResponse(request,'derp/index.html',{})