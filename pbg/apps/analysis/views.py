from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect, Http404,
        HttpResponseForbidden)
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context

import os
import re
from json import dumps

from .forms import (NewProjectForm, ExistingProjectForm, GeneForm,
        ProjectInfoForm, ProjectDirectoryInfoForm, PathologyToggleForm)
from .models import *
from .toolkit.results import ResultsFinder
from .toolkit.dna_parse import (MultipleXMLFilesFoundException,
        ProjectNameNotInMakefileException,
        ImproperlyFormattedXMLFileException)

def _get_project(request, project_name):
    """
    Helper function that returns a project with a given name,
    while taking into account user permissions.

    """
    try:
        project = Project.objects.get(name=project_name)
    except Project.DoesNotExist:
        raise Http404
    if not project in request.user.get_profile().projects.all():
        raise PermissionDenied
    return project


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
def project_list(request):
    """
    The primary analysis dashboard view; displays all projects the user
    is allowed to see.

    """
    queryset = request.user.get_profile().projects.all()
    for project in queryset:
        project.update_progress()
    context = {"projects": queryset.order_by("-name")}
    return render(request, "analysis/project_list.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
def project_detail(request, project_name):
    project = _get_project(request, project_name)
    project.update_progress()
    context = {}
    context["project"] = project

    # Next two lines only included for testing on MM's local machine.
    if not settings.SHOW_RESULTS:
        return render(request, "analysis/project_detail.html", context)

    # Return early if the user is not allowed to see the results tables
    if not request.user.has_perm('analysis.view_project_results'):
        return render(request, "analysis/project_detail.html", context)

    # Accounting for inconsistancy in naming conventions for LA...
    if project.name == "LA":
        results = ResultsFinder(
                project.name, ["LA_Normal", "LA_Tumor"],
                project.cancer_name
                )
    else:
        results = ResultsFinder(
                project.name, [sample.name for sample in project.samples],
                project.cancer_name
                )

    # Get information from the results database tables, if possible
    if results.has_gene_info():
        context["gene_info"] = results.get_gene_info()
    if results.has_variant_info():
        context["variant_info"] = results.get_variant_info()
    if results.has_tier_info():
        tier_name_list = []
        tier_tuple_list = []
        for table in results.results_tables:
            tier1 = results.get_tier_info(1, table)
            tier2 = results.get_tier_info(2, table)
            tier3 = results.get_tier_info(3, table)
            tier_name_list.append(table)
            tier_tuple_list.append((tier1, tier2, tier3))
        context["tier_info"] = zip(tier_name_list, tier_tuple_list)
    return render(request, "analysis/project_detail.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
def project_detail_json(request, project_name):
    project = _get_project(request, project_name)
    project.update_progress()
    res = {"samples":{}}
    for sample in project.samples:
        res["samples"][sample.name] = {}
        res["samples"][sample.name]["origin"] = sample.tissue_of_origin
        res["samples"][sample.name]["RIN"] = sample.rin_score
        if sample.tumor:
            res["samples"][sample.name]["tumor_purity"] = \
                    str(sample.tumor_purity)
            res["samples"][sample.name]["tumor_type"] = sample.tumor_type
            res["samples"][sample.name]["tumor_class"] = sample.tumor_class
    res["bams"] = [bam.name for bam in project.bams]
    res["metrics"] = [metric.name for metric in project.metrics]
    res["vcfs"] = [vcf.name for vcf in project.vcfs]
    return HttpResponse(dumps(res), content_type="application/json")


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
@permission_required('analysis.change_pathology', raise_exception=True)
def pathology_toggle_form(request, project_name):
    project = _get_project(request, project_name)
    if request.method == "POST":
        form = PathologyToggleForm(request.POST, project=project)
        if form.is_valid():
            cd = form.cleaned_data
            pat = re.compile(r"(\d+?)_(.*)")
            for attr, value in cd.items():
                m = pat.match(attr)
                pk = int(m.group(1))
                flavor = m.group(2)
                sample = Sample.objects.get(pk=pk)
                pathology = Pathology.objects.get(sample=sample, flavor=flavor)
                pathology.value = value
                pathology.save()
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        initials = {}
        for sample in project.samples:
            for pathology in sample.pathologies:
                initials["{0}_{1}".format(sample.pk, pathology.flavor)] = \
                        pathology.value
        form = PathologyToggleForm(project=project, initial=initials)
    context = {}
    context["form"] = form
    context["form_value"] = "Submit"
    return render(request, "analysis/form.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
@permission_required('analysis.change_project', raise_exception=True)
def project_info_form(request, project_name):
    project = _get_project(request, project_name)
    if request.method == "POST":
        form = ProjectInfoForm(request.POST, project=project)
        if form.is_valid():
            cd = form.cleaned_data
            cancer_name = cd.pop("cancer_name")
            project.cancer_name = cancer_name
            project.save()
            # this is a little too clever for my liking. -mm
            pat = re.compile(r"(\d+?)_(.*)")
            for attr, value in cd.items():
                m = pat.match(attr)
                pk = int(m.group(1))
                field = m.group(2)
                sample = Sample.objects.get(pk=pk)
                setattr(sample, field, value)
                sample.save()
            return HttpResponseRedirect(reverse("analysis:project_detail",
                    args=(project.name,)))
    else:
        initials = {}
        initials["cancer_name"] = project.cancer_name
        for sample in project.samples:
            if sample.tumor:
                initials["%d_tumor_purity" % sample.pk] = sample.tumor_purity
                initials["%d_tumor_type" % sample.pk] = sample.tumor_type
                initials["%d_tumor_class" % sample.pk] = sample.tumor_class
            initials["%d_tissue_of_origin" % sample.pk] = \
                    sample.tissue_of_origin
            initials["%d_rin_score" % sample.pk] = sample.rin_score
        form = ProjectInfoForm(project=project, initial=initials)
    context = {}
    context["form"] = form
    context["form_value"] = "Submit"
    return render(request, "analysis/form.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
@permission_required('analysis.change_project', raise_exception=True)
def project_directory_info_form(request, project_name):
    project = _get_project(request, project_name)
    if project.bams or project.metrics or project.vcfs:
        msg = "Cannot edit path information once results directory declared"
        messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(project.get_absolute_url())
    if request.method == "POST":
        form = ProjectDirectoryInfoForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            path = cd["path"]
            makefile = cd["makefile"]
            if path:
                project.path = path
            if makefile:
                results_directory = dna_parse.find_results_directory(path,
                        makefile)
                project.results_directory = results_directory
            project.save()
            return HttpResponseRedirect(project.get_absolute_url())
    else:
        initials = {}
        path = project.path
        if path:
            initials["path"] = path
        form = ProjectDirectoryInfoForm(initial=initials)
    context = {}
    context["form"] = form
    context["form_value"] = "Submit"
    return render(request, "analysis/form.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
@permission_required('analysis.add_project', raise_exception=True)
def new_project_form(request):
    if request.method == "POST":
        form = NewProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            project = Project.objects.create_new(cd["project_name"],
                    request.user, keyword=cd["keyword"],
                    cancer_name=cd["cancer_name"], wgs=cd["wgs"],
                    wes=cd["wes"], rna=cd["rna"])
            # Create the project's corresponding samples
            for i in range(1, 5):
                tumor = "tumor_%d" % i
                normal = "normal_%d" % i
                if cd[tumor]:
                    sample = Sample.objects.create_new(name=cd[tumor],
                            project=project, tumor=True)
                if cd[normal]:
                    sample = Sample.objects.create_new(name=cd[normal],
                            project=project)
            return HttpResponseRedirect(reverse("analysis:project_list"))
    else:
        form = NewProjectForm()
    context = {"form":form, "form_value":"Create"}
    return render(request, "analysis/form.html", context)


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
@permission_required('analysis.add_project', raise_exception=True)
def existing_project_form(request):
    if request.method == "POST":
        form = ExistingProjectForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                project = Project.objects.create_existing(cd["path"],
                        request.user, keyword=cd["keyword"],
                        makefile=cd["makefile"], xml_file=cd["xml_file"],
                        wgs=cd["wgs"], wes=cd["wes"], rna=cd["rna"])
            except DirectoryNotFoundException:
                msg = "directory not found."
                form.errors["custom"] = msg
            except DirectoryNotInitializedException:
                msg = "directory doesn't contain both makefile and XML file."
                form.errors["custom"] = msg
            except ResultsDirectoryNotFoundException:
                msg = "results directory not found in directory"
                form.errors["custom"] = msg
            except MultipleXMLFilesFoundException:
                msg = "multiple xml files found in directory"
                form.errors["custom"] = msg
            except ProjectNameNotInMakefileException:
                msg = "project name not listed in makefile"
                form.errors["custom"] = msg
            except ImproperlyFormattedXMLFileException:
                msg = ("could not infer sample names from XML file because "
                       "it is badly formatted")
                form.errors["custom"] = msg
            else:
                return HttpResponseRedirect(reverse("analysis:project_detail",
                        args=(project.name,)))
    else:
        form = ExistingProjectForm()
    context = {"form":form, "form_value":"Create"}
    return render(request, "analysis/form.html", context)


def _create_jbrowse_url(project_name, chromosome, start, stop):
    url = ("http://node3.1425mad.mssm.edu/uziloa01/web/jbrowse/"
           "index.html?data=data/{0}&loc=chr{1}:{2}..{3}"
           "".format(project_name, chromosome, start, stop))
    return url


@login_required
@permission_required('analysis.view_cancer_seq', raise_exception=True)
def gene_form(request, project_name):
    if request.method == "POST":
        form = GeneForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            url = _create_jbrowse_url(project_name, cd["chromosome"],
                    cd["start"], cd["stop"])
            return HttpResponseRedirect(url)
    else:
        form = GeneForm(initial={"project_name":project_name})
    context = {"form":form, "form_value":"Visit JBrowse",
            "js_list":["geneform.js"]}
    return render(request, "form.html", context)


""" NOTE: TO BE ADDED IN A LATER RELEASE. """
#@login_required
#@permission_required('analysis.view_cancer_seq', raise_exception=True)
#def makefile_form(request):
#    if request.method == "POST":
#        form = MakefileForm(request.POST)
#        if form.is_valid():
#            cd = form.cleaned_data
#            #dest = cd['full_path'] # DANGEROUS --- need to talk over
#            dest = "/hpc/users/micchm01/www"
#            dest = os.path.join(dest, "makefile")
#            with open(dest, "w") as out:
#                t = get_template("analysis/makefiletemplate")
#                c = Context(cd)
#                print >>out, t.render(c)
#            return HttpResponseRedirect(reverse("analysis:makefilesubmitted"))
#    else:
#        form = MakefileForm()
#    context = {"form":form, "form_value":"Create"}
#    return render(request, "form.html", context)
#
#
#@login_required
#def makefile_submitted(request):
#    return render(request, "analysis/submitted.html", {"item":"makefile"})
