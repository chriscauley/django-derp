import os, subprocess, sys

DJANGO_SETTINGS_MODULE = "settings"
URLS = []
URL_GROUPS = []
EMAILS = []
PREP_VARIABLES = lambda *args,**kwargs: None
derp_dir = os.path.join(os.path.abspath("."),'_derp')
COMMIT_HASH = subprocess.Popen(['git','rev-parse','HEAD'],stdout=subprocess.PIPE).communicate()[0].strip()
f = os.path.join(derp_dir,"config.py")
exec(compile(open(f).read(),f, 'exec'), globals(), locals())
STABLE = COMMIT_HASH == STABLE_HASH
