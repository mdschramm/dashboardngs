#!/usr/bin/env python
from urllib2 import urlopen
from json import loads


def pull(machine):
    url = "http://node2.1425mad.mssm.edu/sbsuser/web/productionngs/runstatus/json.cgi?name=%s" % machine
    response = urlopen(url)
    return loads(response.read())


def get_runs(machine):
    url = ("http://node2.1425mad.mssm.edu/sbsuser/web/productionngs/"
           "runstatus/runs.cgi?name={0}".format(machine))
    response = urlopen(url)
    return loads(response.read())


def get_run_info(machine_name, run_directory):
    url = ("http://node2.1425mad.mssm.edu/sbsuser/web/productionngs/"
           "runstatus/runs.cgi?name={0}&dir={1}"
           "".format(machine_name, run_directory))
    response = urlopen(url)
    return loads(response.read())


if __name__ == "__main__":
    machine_names = ["Amee", "corey", "Hal", "Sid", "zoe"]
    for machine_name in machine_names:
        print machine_name
        runs = get_runs(machine_name)
        for run in runs:
            print "\t" + run
