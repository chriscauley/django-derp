from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from derp import config, t

class Command (BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument(
            '--stable',
            action='store_true',
            dest='stable',
            help='Accept current code as stable, overwriting all the currently stored results.',
        )
    def handle(self, *args, **options):
        if options['stable']:
            config.CANNONICAL = True
        for email in config.EMAILS:
            t.login(email)
            t.clear(email)
            d = config.PREP_VARIABLES(email)
            for url in config.URLS:
                t.verify_url(url.format(**d),email)