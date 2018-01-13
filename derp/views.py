from django.http import JsonResponse

import subprocess, hashlib

def hash(request):
    status_string,_error = subprocess.Popen(['git','status','-s'],stdout=subprocess.PIPE).communicate()
    diff_string,_error = subprocess.Popen(['git','diff'],stdout=subprocess.PIPE).communicate()
    git_hash, result = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE).communicate()
    unstaged = None
    if status_string or diff_string:
        unstaged = hashlib.md5(status_string + diff_string).hexdigest()
    return JsonResponse({
        'git': git_hash,
        'unstaged': unstaged,
    })