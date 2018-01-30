from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from derp import config, t
from derp.runner import URLRunner

import datetime

class Command (BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument('command_name',nargs='?',type=str)
        parser.add_argument('target',nargs='?',type=str,help="which email group to use")
        parser.add_argument('--missing',action="store_true")
    def print_status(self):
        command_tuples = sorted([(key,value) for key,value in config.COMMANDS.items() if not key.startswith("_")])
        for key,commands in command_tuples:
            print key,'\n'
            print "{0:10.10} ".format(key),len(commands)
        exit()
    def handle(self, *args, **kwargs):
        from _derp.runner import TaskRunner
        command = kwargs['command_name'] or '_all'
        if command == 'status':
            self.print_status()
        targets = config.ALLOWED_TARGETS.get(command,None) # this means a command is limited to these arguments
        targets = targets or config.TARGETS.get(kwargs['target'],kwargs['target']) # or the specified arguments
        targets = targets or config.TARGETS['_all'] # or just use them all!
        if type(targets) == str:
            targets = targets.split(',')
        print "Using commands:",config.COMMANDS.get(command,[])
        print "Using targets:",targets
        today = datetime.date.today()
        for target in targets:
            #t.clear("\n*** Using target %s ***"%target)
            for subcommand in config.COMMANDS.get(command,[]):
                _ = URLRunner if type(subcommand) == str else TaskRunner
                runner = _(subcommand,email=target)
                if kwargs['missing'] and runner.test.testrun_set.filter(commit_id=config.COMMIT_HASH,status="pass",created__gte=today):
                    print "skipping ",runner.test
                    continue
                runner.run()
