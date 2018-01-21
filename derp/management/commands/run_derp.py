from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from derp import config, t

class Command (BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument('command_name',nargs="*",type=str)
        parser.add_argument('--email',help="which email group to use")
        parser.add_argument('--url',help="which email group to use")
        parser.add_argument( #not, this is used as sys.argv in config.py
            '--stable',
            action='store_true',
            dest='stable',
            help='Accept current code as stable, overwriting all the currently stored results.',
        )
    def handle(self, *args, **kwargs):
        commands = kwargs['command_name'] or sorted(config.URL_GROUPS.keys())
        emails = config.EMAILS
        if kwargs['email'] in config.EMAIL_GROUPS:
            emails = config.EMAIL_GROUPS[kwargs['email']]
        elif kwargs['email']:
            emails = [e for e in emails if kwargs['email'] in e]
        print "Using urls:",commands
        print "Using %s emails"%len(emails)
        for email in emails:
            t.login(email)
            t.clear(email)
            for command in commands:
                urls = config.URL_GROUPS[command]
                for url in urls:
                    d = config.PREP_VARIABLES(email=email,url=url)
                    t.verify_url(url,d)