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
HASH_LIST = subprocess.Popen(_cmd.split(" "),stdout=subprocess.PIPE).communicate()[0].split("\n")

def hash(request):
    return JsonResponse({
        'git': config.COMMIT_HASH,
        'unstaged': config.UNSTAGED_HASH or None
    })

def result_json(request):
    hash_list = list(TestStatus.objects.all().values_list("commit_id",flat=True))
    return JsonResponse({
        'teststatuses': {ts.id: ts.as_json for ts in TestStatus.objects.all()},
        'tests': {t.id: t.as_json for t in Test.objects.all()},
        'commit_list': {c.id: c.as_json for c in Commit.objects.filter(id__in=hash_list)},
        'commands': COMMANDS,
        'targets': TARGETS,
    })

def result(request):
    return TemplateResponse(request,'derp/index.html',{})