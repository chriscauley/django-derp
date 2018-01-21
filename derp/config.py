import os, sys

DJANGO_SETTINGS_MODULE = "settings"
URLS = []
URL_GROUPS = []
EMAILS = []
PREP_VARIABLES = lambda *args,**kwargs: None
STABLE="--stable" in sys.argv
derp_dir = os.path.join(os.path.abspath("."),'.derp')

f = os.path.join(derp_dir,"config.py")
exec(compile(open(f).read(),f, 'exec'), globals(), locals())
