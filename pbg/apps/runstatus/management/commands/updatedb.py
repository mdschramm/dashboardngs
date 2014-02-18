from __future__ import print_function

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.runstatus.toolkit.pulljson import get_runs, get_run_info
from apps.runstatus.models import Run

import datetime
import os

# Please note: This script takes a looooooooong time. -MM

class Command(BaseCommand):
    args = '<[machine_name, [run_directory]]>'
    help = 'Updates the run status tables by pulling from node2 json'
    machine_names = ["Amee", "corey", "Hal", "Sid", "zoe"]

    def handle(self, *args, **options):
        if len(args) == 2:
            self.update_run(args[0], args[1])
        elif len(args) == 1:
            self.update_machine(args[0])
        else:
            for machine_name in self.machine_names:
                self.update_machine(machine_name)
        self.update_time()

    def update_machine(self, machine_name):
        for run_directory in get_runs(machine_name):
            self.update_run(machine_name, run_directory)

    def update_run(self, machine_name, run_directory):
        run_info = get_run_info(machine_name, run_directory)
        if not run_info:
            msg = "Run with machine {0} and dir {1} does not exist".format(\
                    machine_name, run_directory)
            raise CommandError(msg)
        try:
            run = Run.objects.get(run_directory=run_directory)
        except Run.DoesNotExist:
            Run.objects.create_from_json(machine_name, run_info)
            self.stdout.write("Added {0} {1}\n".format(machine_name,
                    run_directory))
        else:
            run.update(run_info)
            self.stdout.write("Updated {0} {1}\n".format(machine_name,
                    run_directory))

    def update_time(self):
        now = datetime.datetime.now()
        fmt = now.strftime("%B %d, %Y at %I:%M%p")
        last_updated_file = os.path.join(settings.MEDIA_ROOT, "DB_LAST_UPDATED")
        with open(last_updated_file, "w") as f:
            print(fmt, file=f)
