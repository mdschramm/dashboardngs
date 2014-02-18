from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.loading import get_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .toolkit.parse import ProjectParser, NGSMixin, GeneralAnalysisMixin

from os import listdir, makedirs, symlink, rmdir, unlink
from os.path import dirname, exists, join, split


class Study(models.Model):
    """A general genomics study."""
    name = models.CharField(max_length=255)
    #type = models.CharField(
    #        max_length=15,
    #        choices=settings.STUDY_TYPES,
    #        blank=True)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    """
    A project maps directly to a project directory on Minerva. The
    study type determines what sorts of analyses are run on this
    project, and is a required field. However, only certain values
    are accepted; look in the study_type_table for details.

    """
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    study_type = models.CharField(
            max_length=15,
            choices=settings.STUDY_TYPES,
            blank=True)
    nickname = models.CharField(max_length=255, blank=True)
    studies = models.ManyToManyField(Study, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def sync_with_directory(self, deep=False):
        """
        Creates models to represent information gathered from the project
        directory.

        If the ``deep`` argument is set to True, this calls the
        sync_with_directory method of all project analyses. Otherwise,
        this method doesn't do much; just creates Analysis objects.

        """
        parser = ProjectParser(self.path)
        processed_names = parser.get_processed()
        for name in processed_names:
            analysis, created = Analysis.objects.get_or_create(
                    name=name, project=self)
            if deep:
                analysis.sync_with_directory()


class Sample(models.Model):
    """
    A sample in a project.

    This class will probably get subclassed often, but it is not
    abstract.

    """
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return self.name


class Analysis(models.Model):
    """
    An analysis maps with a ``Processed`` sub-directory in a project
    directory.

    An analysis's pipeline can be determined by parsing the directory
    name. This is done not in Analysis itself, but by a signal.
    Furthermore, the sync_with_directory method is different for
    each pipeline and study type, so each type of analysis needs
    to implement its own sync_with_directory method.

    """
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project)
    samples = models.ManyToManyField(Sample, blank=True, null=True)
    pipeline = models.CharField(max_length=255, blank=True)

    def __init__(self, *args, **kwargs):
        super(Analysis, self).__init__(*args, **kwargs)

        # This is absolutely the worst place to keep this data, but
        # if been running into a bazillion circular import issues.
        # Consider it a temporary fix.
        from apps.cancer.toolkit.parse import CancerMixin
        from apps.cancer.models import CancerAnalysis
        self.pipeline_table = {
            settings.PIPELINE_NGS: NGSMixin,
            settings.PIPELINE_MANUAL: GeneralAnalysisMixin
        }
        self.study_type_table = {
            settings.STUDY_TYPE_CANCER: {
                "mixin": CancerMixin,
                "analysis": CancerAnalysis,
            },
        }
        project = kwargs.get("project")
        if project and project.study_type in self.study_type_table:
            cls = self.study_type_table[project.study_type]["analysis"]
            self.__class__ = cls

    def __unicode__(self):
        return self.project.name + " " + self.name

    def get_parser(self):
        """
        Creates a custom parser object based on pipeline and study_type.

        This is the function that assembles all the parse mixins into
        one coherent whole.

        """
        study_type = self.project.study_type
        try:
            study_type_mixin = self.study_type_table[study_type]["mixin"]
            pipeline_mixin = self.pipeline_table[self.pipeline]
        except KeyError:
            return None
        class CustomParser(study_type_mixin, pipeline_mixin, ProjectParser):
            pass
        return CustomParser(path=self.project.path, name=self.name)

    def sync_with_directory(self):
        """Placeholder function: proxies provide implementation."""
        pass


@receiver(post_save)
def deduce_pipeline(sender, instance, created, **kwargs):
    """Creates the instance.pipeline argument from the instance name."""
    # Just checking if sender == Analysis isn't enough because of all
    # the Analysis proxy classes
    if Analysis in sender.__bases__:
        if created:
            analysis_info = ProjectParser.parse_processed_name(instance.name)
            instance.pipeline = analysis_info["pipeline_name"]
            instance.save()


class _ResultsFile(models.Model):
    """Creates basic fields for the results files."""
    name = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    sample = models.ForeignKey(Sample, blank=True, null=True)
    analysis = models.ForeignKey(Analysis, blank=True, null=True)

    class Meta:
        abstract = True


class BAM(_ResultsFile):
    """A BAM file."""
    pass


class Metric(_ResultsFile):
    """
    A Metric file.

    Because a metric can be viewed from the web, we can place it in
    the /static/ directory. However, we don't want to copy the file
    (too big) so we instead provide a symlink to its original path.
    The static_path argument is a path to the place in the /static/
    directory where the symlink sits.

    """
    static_path = models.CharField(max_length=255, blank=True)

    def create_static_path(self):
        """
        Creates a symbolic link to the metric from the static
        directory, where it can be served to the user.

        If the link already exists, this function deletes the
        previous link and replaces it with a new one.

        """
        if not (self.project and self.analysis):
            return
        dest_path = join(settings.STATIC_ROOT,
                         settings.STATIC_METRIC_LOCATION,
                         self.project.name,
                         self.analysis.name)
        dest_link = join(dest_path, self.name)
        source = join(self.project.path,
                      settings.PROCESSED_DIR_NAME,
                      self.analysis.name,
                      settings.RESULTS_DIR_NAME,
                      self.name)
        if exists(dest_link):
            unlink(dest_link)
        if not exists(dest_path):
            makedirs(dest_path)
        symlink(source, dest_link)
        self.static_path = dest_link
        self.save()

    def remove_static_path(self):
        """Deletes a the symbolic link associated with this Metric."""
        if not self.static_path:
            return
        analysis_path, name = split(self.static_path)
        project_path = dirname(analysis_path)
        if exists(self.static_path):
            unlink(self.static_path)
        if not listdir(analysis_path):
            rmdir(analysis_path)
        if not listdir(project_path):
            rmdir(project_path)


@receiver(post_save, sender=Metric)
def create_symlink(sender, instance, created, **kwargs):
    """An on-create hook to create the symlink_path argument."""
    if created:
        instance.create_static_path()


@receiver(post_delete, sender=Metric)
def delete_symlink(sender, instance, **kwargs):
    """An on-delete hook to delete the symlink from the file system."""
    if instance.static_path:
        instance.remove_static_path()


class VCF(_ResultsFile):
    """A VCF file."""
    pass
