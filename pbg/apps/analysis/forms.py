from django import forms
from .toolkit import dna_parse
import re
import os


class ProjectInfoForm(forms.Form):
    cancer_name = forms.CharField(required=False,
            help_text="Examples: Ovarian, Breast, Pancreatic")
    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project")
        super(ProjectInfoForm, self).__init__(*args, **kwargs)

        # Note: weird reduncancies are necessary to ensure field order
        for sample in project.sample_set.filter(tumor=True):
            self.fields["%d_tissue_of_origin" % sample.pk] = \
                    forms.CharField(required=False,
                    label="%s tissue of origin" % sample.name)
            self.fields["%d_rin_score" % sample.pk] = \
                    forms.DecimalField(required=False,
                    label="%s RIN score" % sample.name)
            self.fields["%d_tumor_purity" % sample.pk] = \
                    forms.DecimalField(required=False, min_value=0,
                    max_value=1, max_digits=3, decimal_places=2,
                    label="%s purity" % sample.name,
                    help_text="Enter a decimal between 0 and 1.")
            self.fields["%d_tumor_type" % sample.pk] = \
                    forms.CharField(required=False,
                    label="%s type" % sample.name)
            self.fields["%d_tumor_class" % sample.pk] = \
                    forms.CharField(required=False,
                    label="%s class" % sample.name)
        for sample in project.sample_set.filter(tumor=False):
            self.fields["%d_tissue_of_origin" % sample.pk] = \
                    forms.CharField(required=False,
                    label="%s tissue of origin" % sample.name)
            self.fields["%d_rin_score" % sample.pk] = \
                    forms.DecimalField(required=False,
                    label="%s RIN score" % sample.name)


class ProjectDirectoryInfoForm(forms.Form):
    path = forms.CharField(required=False)
    makefile = forms.CharField(required=False)

    #def clean_path(self):
    #    path = self.cleaned_data["path"]
    #    if path and not os.path.exists(path):
    #        raise forms.ValidationError("Path not found.")
    #    return path

    #def clean(self):
    #    cleaned_data = super(ProjectDirectoryInfoForm, self).clean()
    #    path = cleaned_data.get("path")
    #    makefile = cleaned_data.get("makefile")
    #    if makefile and not path:
    #        raise forms.ValidationError("Must specify path along with makefile.")
    #    if makefile and not os.path.exists(os.path.join(path, makefile)):
    #        raise forms.ValidationError("Makefile not found.")
    #    if makefile:
    #        results_directory = dna_parse.find_results_directory(path, makefile)
    #        if not results_directory or not os.path.exists(os.path.join(\
    #                path, results_directory)):
    #            raise forms.ValidationError("Results directory not found.")


class PathologyToggleForm(forms.Form):
    """ 
    Creates a form with checkboxes for each analysis type for 
    each sample of a given project.
    """
    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project")
        super(PathologyToggleForm, self).__init__(*args, **kwargs)
        for sample in project.samples:
            for pathology in sample.pathologies:
                self.fields[str(sample.pk) + "_" + pathology.flavor] = \
                        forms.BooleanField(required=False,
                        initial=pathology.value,
                        label="{0} {1}".format(sample.name, pathology.flavor))


class NewProjectForm(forms.Form):
    project_name = forms.CharField()
    keyword = forms.CharField(required=False,
            help_text="Examples: Boston Case, LA")
    cancer_name = forms.CharField(required=False,
            help_text="Examples: Ovarian, Breast, Pancreatic")
    normal_1 = forms.CharField()
    normal_2 = forms.CharField(required=False)
    normal_3 = forms.CharField(required=False)
    normal_4 = forms.CharField(required=False)
    tumor_1 = forms.CharField()
    tumor_2 = forms.CharField(required=False)
    tumor_3 = forms.CharField(required=False)
    tumor_4 = forms.CharField(required=False)
    wgs = forms.BooleanField(label="WGS", required=False)
    wes = forms.BooleanField(label="WES", required=False)
    rna = forms.BooleanField(label="RNA", required=False)


class ExistingProjectForm(forms.Form):
    path = forms.CharField(\
            help_text="Please enter an absolute, not a relative, path")
    keyword = forms.CharField(required=False,
            help_text="Examples: Boston Case, LA")
    xml_file = forms.CharField(required=False, label="XML file")
    makefile = forms.CharField(required=False)
    wgs = forms.BooleanField(label="WGS", required=False)
    wes = forms.BooleanField(label="WES", required=False)
    rna = forms.BooleanField(label="RNA", required=False)


class GeneForm(forms.Form):
    project_name = forms.CharField()
    gene        = forms.CharField(required=False)
    chromlist = [(i, i) for i in range(1, 23)]
    chromlist.append(("x", "x"))
    chromlist.append(("y", "y"))
    chromosome  = forms.ChoiceField(choices=tuple(chromlist))
    start       = forms.CharField()
    stop        = forms.CharField()


"""NOTE: we'll re-add MakefileForm in a later release."""
#class MakefileForm(forms.Form):
#    """Validation worked on."""
#    defaultpath = "/projects/PBG/dashboardngs/django/"
#    full_path       = forms.CharField(initial=defaultpath)
#    project         = forms.CharField()
#    xml             = forms.CharField(label="XML")
#    pipelinechoices = (("GENOME", "Genome"),
#                       ("EXOME", "Exome"),
#                       ("TARGETED", "Targeted"),)
#    pipeline        = forms.ChoiceField(choices=pipelinechoices)
#    tumor_purity    = forms.CharField()
#    interval        = forms.CharField()
#    bait_interval   = forms.CharField()
#    scatter_gather  = forms.CharField(initial="20", label="Scatter-gather")
#    threads         = forms.CharField(initial="16")
#    walltime        = forms.CharField(initial="24:00:00")
#
#    def clean_xml(self):
#        """Checks to see if a given xml filename is valid."""
#        xml = self.cleaned_data['xml']
#        pat = re.compile(r'^[\w\d]+\.xml')
#        m = pat.search(xml)
#        if not m:
#            raise forms.ValidationError("Filename must have only numbers, letters, and/or underscores, and must end in .xml")
#        return xml
#
#    def clean_tumor_purity(self):
#        """Checks to see if tumor_purity is between 0 and 1, and goes to the hundreth."""
#        tumor_purity = self.cleaned_data['tumor_purity']
#        pat = re.compile(r'^0?\.\d\d$')
#        m = pat.search(tumor_purity)
#        if not m:
#            raise forms.ValidationError("Tumor purity must be between 0 and 1 and must have exactly 2 significant figures.""")
#        return tumor_purity
#
#    def clean_scatter_gather(self):
#        """Checks to see if scatter_gather is an integer between 0 and 64."""
#        scatter_gather = self.cleaned_data['scatter_gather']
#        #pat = re.compile(r'^([0-5]?\d)|(6[0-4])$')
#        pat = re.compile(r'^\d?\d$')
#        m = pat.search(scatter_gather)
#        if not m:
#            #raise forms.ValidationError("Scatter-gather must be an integer between 0 and 64.")
#            raise forms.ValidationError("Scatter-gather must be an integer between 0 and 99.")
#        return scatter_gather
#
#    def clean_threads(self):
#        """Checks to see if threads is an integer between 0 and 64."""
#        threads = self.cleaned_data['threads']
#        #pat = re.compile(r'^[0-5]?\d|6[0-4]$')
#        pat = re.compile(r'^\d?\d$')
#        m = pat.match(threads)
#        if not m:
#            #raise forms.ValidationError("Threads must be an integer between 0 and 64.")
#            raise forms.ValidationError("Threads must be an integer between 0 and 99.")
#        return threads
#
#    def clean_walltime(self):
#        """Checks to see if walltime is of the format (h)hh:mm:ss, and is at most 199 h, 59 m, 59 s."""
#        walltime = self.cleaned_data['walltime']
#        pat = re.compile(r'^[01]?\d\d:[0-5]\d:[0-5]\d$')
#        m = pat.search(walltime)
#        if not m:
#            raise forms.ValidationError("Walltime must be of the format (h)hh:mm:ss, and be at most 199 h, 59 m, 59 s.""")
#        return walltime
#
#    
#
