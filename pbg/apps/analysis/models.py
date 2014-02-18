from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from .toolkit import dna_parse, rna_parse
from apps.runstatus.models import Sample as RunStatusSample

import os

class DirectoryNotInitializedException(Exception):
    pass


class DirectoryNotFoundException(Exception):
    pass


class ResultsDirectoryNotFoundException(Exception):
    pass


class ProjectManager(models.Manager):
    def current_version(self, name):
        """Calculates the most recent version of a project, given its name."""
        allversions = \
                super(ProjectManager, self).get_query_set().filter(name=name)
        if not allversions:
            return 0
        return max([version.version for version in allversions])

    def next_version(self, name):
        """Calculates the most next version of a project, given its name."""
        return self.current_version(name) + 1

    def get(self, **kwargs):
        """
        Augments default get() function with automatic most-recent-version
        calculation.
        """
        if not "version" in kwargs:
            qs = super(ProjectManager, self).get_query_set().filter(**kwargs)
            # Make sure something was returned.
            if not qs:
                raise Project.DoesNotExist
            # Make sure only projects of the same name were returned.
            projectname = qs[0].name
            for project in qs:
                if project.name != projectname:
                    raise Project.MultipleObjectsReturned
            # Find the project with the highest version.
            highestversion = -1
            bestproject = None
            for project in qs:
                if project.version > highestversion:
                    highestversion = project.version
                    bestproject = project
            return bestproject
        else:
            return super(ProjectManager, self).get(**kwargs)

    def create_new(self, name, user, keyword="", cancer_name="", wgs=False,
            wes=False, rna=False):
        """Creates a projet from the given data."""
        version = Project.objects.next_version(name)
        # Create a new project with form information
        project = Project.objects.create(name=name, version=version,
                wgs=wgs, wes=wes, rna=rna)
        # Add the project to the current user profile, and all staff user
        # profiles
        project.add_to_profiles(user)
        return project

    def create_existing(self, path, user, keyword="", makefile="",
            xml_file="", cancer_name="", wgs=False, wes=False, rna=False):
        """
        Given a project_dir_path, adds the given project to the
        database. This function also creates associated Sample objects
        and Pathology objects, but not SequencingInfo objects. This
        function can throw the following exceptions:

        DirectoryNotFoundException
            - path does not exist
        DirectoryNotInitializedException
            - the path doesn't contain a clearly specified makefile and XML file
        ResultsDirectoryNotFoundException
            - the path doesn't contain a results directory
        dna_parse.MultipleXMLFilesFoundException
            - if the XML file is not specified as an argument, the parser
              will try to find one in the directory; if it finds multiple,
              it raises this exception
        dna_parse.ProjectNameNotInMakefileException
            - the given (or discovered) makefile does not contain the
              PROJECT argument
        dna_parse.ImproperlyFormattedXMLFileException
            - the XML file with the sample names is not properly formatted
        """
        if not os.path.exists(path):
            raise DirectoryNotFoundException()
        if not makefile:
            makefile = dna_parse.find_makefile(path)
        if not xml_file:
            try:
                xml_file = dna_parse.find_xml_file(path)
            except dna_parse.MultipleXMLFilesFoundException:
                raise
        if not makefile or not xml_file:
            raise DirectoryNotInitializedException()
        results_directory = dna_parse.find_results_directory(path, makefile)
        if not results_directory:
            raise ResultsDirectoryNotFoundException()
        try:
            project_name = dna_parse.get_project_name(path, makefile)
        except dna_parse.ProjectNameNotInMakefileException:
            raise
        version = Project.objects.next_version(project_name)
        project = Project.objects.create(name=project_name,
                keyword=keyword, path=path,
                results_directory=results_directory, version=version,
                cancer_name=cancer_name, wgs=wgs, wes=wes, rna=rna)
        try:
            Sample.objects.create_from_project(project, xml_file)
        except dna_parse.ImproperlyFormattedXMLFileException:
            project.delete()
            raise
        project.add_to_profiles(user)
        return project


class Project(models.Model):
    name = models.CharField(max_length=256)
    keyword = models.CharField(max_length=256, blank=True)
    path = models.CharField(max_length=256, blank=True)
    results_directory = models.CharField(max_length=256, blank=True)
    version = models.SmallIntegerField()
    cancer_name = models.CharField(max_length=256, blank=True)
    done = models.BooleanField()
    wgs = models.BooleanField()
    wes = models.BooleanField()
    rna = models.BooleanField()
    #sequenced = models.BooleanField()

    objects = ProjectManager()

    class Meta:
        permissions = (
            ("view_cancer_seq", "Can view the cancer seq dashboard"),
            ("view_project_results", "Can view the results tables"),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("analysis:project_detail", args=(self.name,))

    @property
    def samples(self):
        return self.sample_set.all()

    @property
    def bams(self):
        return self.bam_set.all()

    @property
    def metrics(self):
        return self.metric_set.all()

    @property
    def vcfs(self):
        return self.vcf_set.all()

    @property
    def results_directory_path(self):
        return os.path.join(self.path, self.results_directory)

    @property
    def metrics_directory_path(self):
        return os.path.join(settings.STATIC_ROOT, "metrics", str(self.pk))

    def add_to_profiles(self, user=None):
        if user:
            self.add_to_user_profile(user)
        self.add_to_admin_profiles()
        if self.name.startswith("PT") or self.name.startswith("pt"):
            self.add_to_group_profiles("Ovarian")
        else:
            self.add_to_group_profiles("Personalized Cancer")

    def add_to_user_profile(self, user):
        """Adds the current project to the user's project portfolio."""
        profile = user.get_profile()
        if not profile in profile.projects.all():
            profile.projects.add(self)

    def add_to_admin_profiles(self):
        """Adds the current project to all admin's project portflios."""
        for admin in User.objects.filter(is_staff=True):
            self.add_to_user_profile(admin)

    def add_to_group_profiles(self, group):
        for user in User.objects.filter(groups__name=group):
            self.add_to_user_profile(user)

    def update_progress(self):
        """
        Uses the dna_parse.py helper script to check for new BAMs, metrics,
        or VCFs. That is, it will update the calling model with the most
        current information.
        """
        if self.done:
            return
        # please delete these next three lines
        for sample in self.samples:
            for sequencing_info in sample.sequencing_infos:
                sequencing_info.find_run_status_sample()
        if not self.path or not self.results_directory:
            return
        sample_names = [sample.name for sample in self.samples]
        if not self.bams and dna_parse.is_bam_done(self.results_directory_path,
                self.name):
            bam_info = dna_parse.get_bams(self.results_directory_path,
                    self.name, sample_names)
            for sample_name, bam in bam_info.items():
                sample = Sample.objects.get(name=sample_name, project=self)
                BAM.objects.create(name=bam, project=self, sample=sample)
        Metric.objects.create_dna_from_project(self)
        Metric.objects.create_rna_from_project(self)
        VCF.objects.create_from_project(self)
        if self.bams and self.metrics and self.vcfs:
            for sample in self.samples:
                if sample.tumor and not sample.rna_metrics_found:
                    return
            self.done = True
            self.save()


@receiver(models.signals.post_delete, sender=Project)
def project_delete(sender, instance, **kwargs):
    """
    Removes all the symlinks of the project's metrics.
    
    This signal is associated with Project instead of Metric because
    a) Project gets deleted before Metric does, and b) Metric needs
    to know Project's primary key to find its associated symlink.

    """
    if os.path.exists(instance.metrics_directory_path):
        for file_name in os.listdir(instance.metrics_directory_path):
            file_path = os.path.join(instance.metrics_directory_path, file_name)
            if os.path.isdir(file_path):
                for symlink in os.listdir(file_path):
                    symlink_path = os.path.join(file_path, symlink)
                    os.remove(symlink_path)
                os.rmdir(file_path)
            else:
                os.remove(file_path)
        os.rmdir(instance.metrics_directory_path)


class SampleManager(models.Manager):
    def create_new(self, name, project, tumor=False):
        # Create the sample.
        sample = Sample.objects.create(name=name, project=project, tumor=tumor)
        # Create the samples' corresponding pathology and sequencing info
        # objects.
        Pathology.objects.create_from_sample(sample=sample)
        SequencingInfo.objects.create_from_sample(sample=sample)
        return sample

    def create_from_project(self, project, xml_file):
        try:
            samples_in_path = dna_parse.get_sample_names(project.path, xml_file)
        except dna_parse.ImproperlyFormattedXMLFileException:
            raise
        samples_in_database = []
        for sample_name in samples_in_path:
            # Really crappy distinguisher... needs serious improvement.
            if "tumor" in sample_name.lower() or "recurrent" in sample_name.lower() or \
                    "primary" in sample_name.lower():
                sample = Sample.objects.create(name=sample_name,
                        project=project, tumor=True)
            else:
                sample = Sample.objects.create(name=sample_name,
                        project=project)
            samples_in_database.append(sample)
        for sample in samples_in_database:
            Pathology.objects.create_from_sample(sample=sample)
        return samples_in_database


class Sample(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    tissue_of_origin = models.CharField(max_length=256, blank=True)
    rin_score = models.DecimalField(max_digits=3, decimal_places=1,
            blank=True, null=True)
    tumor = models.BooleanField()
    # the following four fields are only defined if tumor == True
    tumor_purity = models.DecimalField(max_digits=3, decimal_places=2,
            blank=True, null=True)
    tumor_type = models.CharField(max_length=256, blank=True)
    tumor_class = models.CharField(max_length=256, blank=True)
    rna_metrics_found = models.BooleanField()

    objects = SampleManager()

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.project.get_absolute_url()

    @property
    def sequencing_infos(self):
        return self.sequencinginfo_set.all()

    @property
    def pathologies(self):
        return self.pathology_set.all()

    @property
    def total_cycles(self):
        if self.sequencing_infos.count():
            return self.sequencing_infos[0].total_cycles
        return None

    @property
    def current_cycle(self):
        if not self.total_cycles:
            return None
        if self.sequencing_infos.count():
            return self.sequencing_infos[0].current_cycle
        return None

    @property
    def sequencing_info_wgs(self):
        try:
            return SequencingInfo.objects.get(sample=self, flavor="wgs")
        except SequencingInfo.DoesNotExist:
            return None

    @property
    def sequencing_info_wes(self):
        try:
            return SequencingInfo.objects.get(sample=self, flavor="wes")
        except SequencingInfo.DoesNotExist:
            return None

    @property
    def sequencing_info_rna(self):
        try:
            return SequencingInfo.objects.get(sample=self, flavor="rna")
        except SequencingInfo.DoesNotExist:
            return None

    @property
    def pathology_dna(self):
        try:
            return Pathology.objects.get(sample=self, flavor="dna")
        except Pathology.DoesNotExist:
            return None

    @property
    def pathology_rna(self):
        try:
            return Pathology.objects.get(sample=self, flavor="rna")
        except Pathology.DoesNotExist:
            return None

    
    @property
    def bam_status(self):
        if not settings.SHOW_RESULTS:
            return "Not on Minerva"
        if not os.path.exists(self.project.results_directory_path):
            return "FASTQs Not Ready."
        return dna_parse.get_bam_status(self.project.results_directory_path,
                self.project.name, self.name)


    @property
    def metric_status(self):
        if not settings.SHOW_RESULTS:
            return "Not on Minerva"
        if not os.path.exists(self.project.results_directory_path):
            return "FASTQs Not Ready."
        return dna_parse.get_metric_status(self.project.results_directory_path,
                self.project.name, self.name)

    @property
    def vcf_status(self):
        if not settings.SHOW_RESULTS:
            return "Not on Minerva"
        if not os.path.exists(self.project.results_directory_path):
            return "FASTQs Not Ready."
        if self.tumor:
            return dna_parse.get_vcf_status(\
                    self.project.results_directory_path,
                    self.project.name,
                    self.name)
        else:
            return dna_parse.get_project_vcf_status(\
                    self.project.results_directory_path,
                    self.project.name)

    @property
    def rna_metric_status(self):
        if self.rna_metrics_found:
            return "Done."
        return "Not done."

    @property
    def rna_metric_path(self):
        try:
            path = rna_parse.get_qc_path(self.name)
        except IOError:
            return None
        return path

    @property
    def sequenced(self):
        """
        Boolean tester to see if the sample has been fully sequenced
        or not.  We return True when the sample has no associated
        sequencing info objects. This seems counter-intuitive, but
        the only way a sample could have no sequencing info objects
        is if it were entered as part of a pre-sequenced project
        (meaning the sequencing has already been done).
        """
        sequencing_infos = self.sequencinginfo_set.all()
        if not sequencing_infos:
            return True
        for sequencing_info in sequencing_infos:
            if not sequencing_info.fastq_ready:
                return False
        return True


class PathologyManager(models.Manager):
    def create_from_sample(self, sample):
        # Before doing anything, make sure pathology objects don't
        # already exist
        qs = Pathology.objects.filter(sample=sample)
        if qs:
            return
        res = []
        if sample.project.wgs or sample.project.wes:
            res.append(Pathology.objects.create(flavor="dna", sample=sample))
        if sample.tumor and sample.project.rna:
            res.append(Pathology.objects.create(flavor="rna", sample=sample))
        return res


class Pathology(models.Model):
    value = models.BooleanField()
    flavor = models.CharField(max_length=16)
    sample = models.ForeignKey(Sample)

    objects = PathologyManager()

    def __unicode__(self):
        return self.sample.name + " " + self.flavor

    def get_absolute_url(self):
        return self.project.sample.get_absolute_url()


class SequencingManager(models.Manager):
    def create_from_sample(self, sample):
        # Before doing anything, make sure sequencing info objects don't
        # already exist
        qs = SequencingInfo.objects.filter(sample=sample)
        if qs:
            for info in qs:
                info.find_run_status_sample()
            return
        sequencing_objects = []
        if sample.project.wgs:
            info = SequencingInfo.objects.create(sample=sample, flavor="wgs")
            sequencing_objects.append(info)
        if sample.project.wes:
            info = SequencingInfo.objects.create(sample=sample, flavor="wes")
            sequencing_objects.append(info)
        if sample.tumor and sample.project.rna:
            info = SequencingInfo.objects.create(sample=sample, flavor="rna")
            sequencing_objects.append(info)
        for info in sequencing_objects:
            info.find_run_status_sample()
        return sequencing_objects


class SequencingInfo(models.Model):
    sample = models.ForeignKey(Sample)
    run_status_sample = models.OneToOneField('runstatus.Sample', blank=True,
            null=True)
    flavor = models.CharField(max_length=16, blank=True)

    objects = SequencingManager()

    def __unicode__(self):
        if self.run_status_sample:
            return self.run_status_sample.name
        else:
            return unicode(self.id)

    def get_absolute_url(self):
        return self.project.sample.get_absolute_url()

    def find_run_status_sample(self):
        if self.run_status_sample:
            return
        sample_name = self.sample.name
        regex = r"{0}_{1}".format(sample_name, self.flavor)
        run_status_samples = RunStatusSample.objects.filter(name__iregex=regex)
        # There may be multiple run status samples; just take the first one
        if run_status_samples:
            self.run_status_sample = run_status_samples[0]
            self.save()

    @property
    def current_cycle(self):
        run = self.run_status_sample.project.sample_sheet.run
        return run.current_cycle

    @property
    def total_cycles(self):
        run = self.run_status_sample.project.sample_sheet.run
        return run.total_cycles

    @property
    def fastq_ready(self):
        project = self.run_status_sample.project
        return project.fastq_ready

    @property
    def sequencing_done(self):
        run = self.run_status_sample.project.sample_sheet.run
        return run.total_cycles == run.current_cycle

    @property
    def run(self):
        return self.run_status_sample.project.sample_sheet.run


    @property
    def tooltip_text(self):
        return "Cycle {0}/{1} on {2} #{3}.".format(self.current_cycle,
                self.total_cycles, self.run.machine_name, self.run.run_number)


class BAM(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    sample = models.ForeignKey(Sample, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.project.get_absolute_url()


class MetricManager(models.Manager):
    """
    Metrics are trickier than BAMs or VCFs because Metrics have an
    associated symlink that lives in the static/metrics directory.
    Whenever a metric is created, you have to make sure to create
    the symlink, and whenever a metric is deleted, you have to make
    sure to delete it.
    """

    def get_or_create(self, name, project, sample=None, rna=False):
        """
        Overrides the standard get_or_create by calling create_or_symlink
        instead of vanilla create.
        """
        try:
            metric = Metric.objects.get(name=name, project=project,
                                        sample=sample, rna=rna)
        except Metric.DoesNotExist:
            metric = self.create_and_symlink(name, project, sample, rna)
        return metric

    def create_dna_from_project(self, project):
        """
        Uses the get_metrics function in the dna_parse toolkit
        script in order to discover and create the metric files in
        the results directory. You can call this function as many
        times as you want with no penalty; because it calls the
        get_or_create manager method, you can be assured that
        discovered Metric objects will only be added to the database
        once.

        Returns all metrics found in the results directory.
        """
        res = []
        sample_names = [sample.name for sample in project.samples]
        metric_info = dna_parse.get_metrics(project.results_directory_path,
                project.name, sample_names)
        for metric_name in metric_info[project.name]:
            metric = self.get_or_create(metric_name, project)
            res.append(metric)
        for sample_name, metric_list in metric_info["samples"].items():
            sample = Sample.objects.get(name=sample_name, project=project)
            for metric_name in metric_list:
                metric = self.get_or_create(metric_name, project, sample)
                res.append(metric)
        return res

    def create_rna_from_project(self, project):
        """
        Uses the get_metrics function in the rna_parse toolkit
        script in order to discover and create the metric files in
        the results directory. Unlike with dna_parse, the rna_parse
        script only returns the metric files when it knows that all
        of them have been created, and this information is stored
        as a boolean toggle in the Sample model. For these reason,
        this function does not need to use get_or_create as
        long as it checks that sample.rna_metrics_found == False.

        Returns only the newly created metrics, unlike
        create_dna_from_project. Maybe this is worth a rewrite?
        """
        res = []
        for sample in project.samples:
            sample_metrics = []
            if sample.rna_metrics_found or not sample.tumor:
                continue
            metric_info = rna_parse.get_metrics(sample.name)
            if not metric_info:
                continue
            index_name = metric_info["index"]
            if not Metric.objects.filter(name=index_name, project=project,
                                         sample=sample):
                metric = self.create_and_symlink(index_name, project, sample,
                                                 rna=True)
                sample_metrics.append(metric)
            three_prime_info = metric_info["three_prime"]
            for ext, name in three_prime_info.items():
                if not Metric.objects.filter(name=name, project=project,
                        sample=sample):
                    metric = self.create_and_symlink(name, project, sample,
                            rna=True)
                    sample_metrics.append(metric)
            if sample_metrics:
                sample.rna_metrics_found = True
                sample.save()
                res.extend(sample_metrics)
        return res

    def create_and_symlink(self, metric_name, project, sample=None, rna=False):
        """
        Creates a metric object with the given info, and then creates
        a symlink for that metric.
        """
        metric = Metric.objects.create(name=metric_name, project=project,
                                       sample=sample, rna=rna)
        metric.create_symlink()
        return metric


class Metric(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    sample = models.ForeignKey(Sample, blank=True, null=True)
    rna = models.BooleanField()

    objects = MetricManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.project.get_absolute_url()

    def create_symlink(self):
        if self.rna:
            source_path = os.path.join(self.sample.rna_metric_path, self.name)
        else:
            source_path = os.path.join(self.project.path,
                    self.project.results_directory, self.name)
        dest_path = os.path.join(settings.STATIC_ROOT, "metrics/",
                str(self.project.pk))
        if self.sample:
            dest_path = os.path.join(dest_path, self.sample.name)
        dest_link = os.path.join(dest_path, self.name)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        if os.path.exists(dest_link):
            os.unlink(dest_link)
        os.symlink(source_path, dest_link)

    @property
    def symlink_url(self):
        symlink_path = os.path.join(settings.STATIC_URL, "metrics",
                str(self.project.pk))
        if self.sample:
            symlink_path = os.path.join(symlink_path, self.sample.name)
        return os.path.join(symlink_path, self.name)

    dna_classifications = [
            ("insert", "Inserts"), ("gc", "GCs"),
            ("quality", "Quality Scores"), ("variant", "Variant Metrics"),
            ]
    rna_classifications = [("rna", "RNA"), ("three_prime", "3' Bias")]
    classifications = dna_classifications + rna_classifications + \
            [("other", "Other")]
    classification_patterns = {
            "index.html":"rna",
            "meancoverage_medium":"three_prime",
            "insert":"insert",
            "gc_":"gc",
            "quality":"quality",
            "snp":"variant",
            "ind":"variant",
            "varscan":"variant",
            "crest":"variant"
            }

    @property
    def classification(self):
        name = self.name.lower()
        for pattern, classification in self.classification_patterns.items():
            if pattern in name:
                return classification
        return "other"

class VCFManager(models.Manager):
    def create_from_project(self, project):
        """VCF equivalent of same method in MetricManager"""
        res = []
        sample_names = [sample.name for sample in project.samples]
        vcf_info = dna_parse.get_vcfs(project.results_directory_path,
                project.name, sample_names)
        for vcf_name in vcf_info[project.name]:
            vcf = VCF.objects.get_or_create(name=vcf_name, project=project)
            res.append(vcf)
        for sample_name, vcf_list in vcf_info["samples"].items():
            sample = Sample.objects.get(name=sample_name, project=project)
            for vcf_name in vcf_list:
                vcf = VCF.objects.get_or_create(name=vcf_name, project=project,
                                                sample=sample)
                res.append(vcf)
        return res


class VCF(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    sample = models.ForeignKey(Sample, blank=True, null=True)

    objects = VCFManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("analysis:project_detail", args=(self.project.name,))
