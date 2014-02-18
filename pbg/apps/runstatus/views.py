from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render

from .models import Run
from .forms import Node2Form, RunAbortedForm

import os
from urllib2 import urlopen


@login_required
@permission_required('runstatus.view_run', raise_exception=True)
def run_status(request, machine):
    # lamenting our institutional capitalization inconsistency...
    if machine == "Corey" or machine == "Zoe":
        machine = machine.lower()
    elif machine == "amee" or machine == "hal" or machine == "sid":
        machine = machine.capitalize()
    # not strictly necessary to check, but it makes me feel good inside
    validmachines = ["Amee", "corey", "Hal", "Sid", "zoe"]
    if not machine in validmachines:
        raise Http404
    runs = Run.objects.filter(machine_name=machine)
    last_updated_file = os.path.join(settings.MEDIA_ROOT, "DB_LAST_UPDATED")
    try:
        with open(last_updated_file) as f:
            last_updated = f.readline().strip()
    except IOError:
        last_updated = ""
    context = {"runs":runs, "machine":machine, "machines":validmachines,
            "last_updated":last_updated}
    return render(request, "runstatus/run_list.html", context)


@permission_required('runstatus.view_run', raise_exception=True)
def mark_as_aborted(request, machine, run_id):
    back_url = reverse("run_status:run_status", args=(machine,))
    if request.method == "POST":
        form = RunAbortedForm(request.POST)
        try:
            run = Run.objects.get(pk=run_id)
        except Run.DoesNotExist:
            msg = "Error: that run does not exist."
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(back_url)
        else:
            run.aborted = True
            run.save()
            msg = "Run marked as aborted."
            messages.add_message(request, messages.INFO, msg)
            return HttpResponseRedirect(back_url)
    else:
        form = RunAbortedForm()
    context = {}
    context["back_url"] = back_url
    context["form"] = form
    return render(request, "runstatus/confirm_run_abort.html", context)



def _construct_node2_url(machine, run_directory, run_number, sample_sheet,
        action):
    rundir = "/home/sbsuser/{0}/Runs/{1}".format(machine, run_directory)
    url = ("http://node2.1425mad.mssm.edu/sbsuser/web/productionngs/runstatus/"
           "postdb.cgi?rundir={0}&runnum={1}&samplesheet={2}&action={3}"
           "".format(rundir, run_number, sample_sheet, action))
    return url


def send_info_to_node2(request):
    if request.method == "POST":
        form = Node2Form(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            url = _construct_node2_url(
                    cd["machine_name"], cd["run_directory"], cd["run_number"],
                    cd["sample_sheet"], cd["action"],
                    )
            urlopen(url)
            return HttpResponseRedirect(reverse("run_status:run_status"))
    else:
        form = Node2Form()
    context = {"form":form, "form_value":"Submit"}
    return render(request, "runstatus/form.html", context)
