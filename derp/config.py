import os, subprocess, sys, hashlib

DJANGO_SETTINGS_MODULE = "settings"
TARGETS = {}
COMMANDS = {}
ALLOWED_TARGETS = {}
_process_json = PREP_VARIABLES = lambda *args,**kwargs: None
derp_dir = os.path.join(os.path.abspath("."),'_derp')


_cmd = 'git log --pretty=format:%H'
COMMIT_LIST = subprocess.Popen(_cmd.split(" "),stdout=subprocess.PIPE).communicate()[0].split("\n")
COMMIT_HASH = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE).communicate()[0].strip()
diff_string,_error = subprocess.Popen(['git','diff'],stdout=subprocess.PIPE).communicate()
UNSTAGED_HASH = diff_string and hashlib.md5(diff_string).hexdigest() # empty string or a hash of the unstaged code
f = os.path.join(derp_dir,"config.py")
exec(compile(open(f).read(),f, 'exec'), globals(), locals())
STABLE = UNSTAGED_HASH + COMMIT_HASH == STABLE_HASH
