from django.conf import settings
from django.contrib.auth import get_user_model
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
        from _derp.runner import TaskRunner
        command = kwargs['command_name'] or '_all'
        try:
            testgroup = TestGroup.objects.get(name=kwargs['command_name'])
        except TestGroup.DoesNotExist:
            testgroup = None
        if command == 'status':
            self.print_status()
        targets = config.ALLOWED_TARGETS.get(command,None) # this means a command is limited to these arguments
        targets = targets or config.TARGETS.get(kwargs['target'],kwargs['target']) # or the specified arguments
        targets = targets or config.TARGETS['_all'] # or just use them all!
        commands = config.COMMANDS.get(command,[command])
        if type(targets) == str:
            targets = targets.split(',')
        if kwargs['ncommands']:
            commands = commands[:kwargs['ncommands']]
        if kwargs['ntargets']:
            targets = targets[:kwargs['ntargets']]
        if config.UNSTAGED_HASH:
            print "\n\nCANNOT SAVE RESULTS DUE TO UNSTAGED COMMITS\n\n"
        print "Using commands:",commands
        print "Using targets:",targets
        today = datetime.date.today()
        skipped = 0
        for target in targets:
            #t.clear("\n*** Using target %s ***"%target)
            for subcommand in commands:
                _ = URLRunner if type(subcommand) == str else TaskRunner
                runner = _(subcommand,email=target,testgroup=testgroup)
                if kwargs['missing'] and runner.test.testrun_set.filter(commit_id=config.COMMIT_HASH,status="pass",created__gte=today):
                    skipped += 1
                    continue
                runner.run()
        if config.UNSTAGED_HASH:
            print "\n\nCANNOT SAVE RESULTS DUE TO UNSTAGED COMMITS"
        if skipped:
            print "Skipped %s tests due to --missing"%skipped
