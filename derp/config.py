import os, argparse

DJANGO_SETTINGS_MODULE = "settings"
URLS = []
EMAILS = []
PREP_VARIABLES = lambda *args,**kwargs: None
CANNONICAL=os.environ.get("CANNONICAL",False)
derp_dir = os.path.join(os.path.abspath("."),'.derp')

f = os.path.join(derp_dir,"config.py")
exec(compile(open(f).read(),f, 'exec'), globals(), locals())
