from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf.urls import RegexURLPattern, RegexURLResolver
from django.core.urlresolvers import get_resolver
from django.core.management.base import BaseCommand

from derp import config, t
from derp.runner import URLRunner
from derp.models import TestGroup

import datetime

class Command (BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument('command_name',nargs='?',type=str)
        parser.add_argument('target',nargs='?',type=str,help="which email group to use")
        parser.add_argument('--missing',action="store_true")
        parser.add_argument("-ntargets",nargs='?',type=int,help="number of targets to use")
        parser.add_argument("-ncommands",nargs='?',type=int,help="number of commands to use")
    def print_status(self):
        command_tuples = sorted([(key,value) for key,value in config.COMMANDS.items() if not key.startswith("_")])
        for key,commands in command_tuples:
            print key,'\n'
            print "{0:10.10} ".format(key),len(commands)
        exit()
    def handle(self, *args, **kwargs):
        urls = get_resolver(None)
        all_urls = list()

        def func_for_sorting(i):
            if i.name is None:
                i.name = ''
            return i.name

        def show_urls(urls):
            for url in urls.url_patterns:
                if isinstance(url, RegexURLResolver):
                    show_urls(url)
                elif isinstance(url, RegexURLPattern):
                    all_urls.append(url)

        show_urls(urls)
        all_urls.sort(key=func_for_sorting, reverse=False)
        for url in all_urls:
            print url.name
            print dir(url)
            return