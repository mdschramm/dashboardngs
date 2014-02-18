from django.conf import settings
from django.test import TestCase
from os.path import exists, join
from inspect import getmro

from ..models import Study, Project, Sample, Analysis, BAM, Metric, VCF
from ..toolkit.parse import NGSMixin, GeneralAnalysisMixin, ProjectParser
from apps.cancer.toolkit.parse import CancerMixin
from apps.cancer.models import CancerAnalysis

class TestProject(TestCase):
    def setUp(self):
        self.name = "PT000"
        self.path = join(settings.TEST_DIRECTORY, self.name)
        self.project = Project.objects.create(
                name=self.name, path=self.path,
                study_type=settings.STUDY_TYPE_CANCER)

    def test_sync_with_directory(self):
        # Test without ``deep`` (i.e. nothing is created besides analyses)
        # (``deep`` tests are specific to analysis types, e.g. cancer)
        project = self.project
        project.sync_with_directory()
        self.assertTrue(Analysis.objects.filter(project=project).count())
        self.assertFalse(Sample.objects.filter(project=project).count())
        self.assertFalse(BAM.objects.filter(project=project).count())
        self.assertFalse(Metric.objects.filter(project=project).count())
        self.assertFalse(VCF.objects.filter(project=project).count())

class TestAnalysis(TestCase):
    def setUp(self):
        self.project_name = "PT000"
        self.project_path = join(settings.TEST_DIRECTORY, self.project_name)
        self.project = Project.objects.create(
                name=self.project_name, path=self.project_path,
                study_type=settings.STUDY_TYPE_CANCER)
        self.complete_analysis_name = "Ngs.2_5_2"
        self.manual_analysis_name = "ManualSpecial.2013_08_21"

        self.complete_analysis = Analysis.objects.create(
                name=self.complete_analysis_name, project=self.project)
        self.manual_analysis = Analysis.objects.create(
                name=self.manual_analysis_name, project=self.project)

    def test_sync_with_directory(self):
        pass

    def test_proxy_class_magic(self):
        """
        TODO: better tests
        """
        self.assertEqual(self.complete_analysis.__class__, CancerAnalysis)
        self.assertEqual(self.manual_analysis.__class__, CancerAnalysis)

    def test_get_parser(self):
        complete_analysis_parser = self.complete_analysis.get_parser()
        correct_bases = (CancerMixin, NGSMixin, ProjectParser)
        bases = complete_analysis_parser.__class__.__bases__
        self.assertEqual(correct_bases, bases)

        manual_analysis_parser = self.manual_analysis.get_parser()
        correct_bases = (CancerMixin, GeneralAnalysisMixin, ProjectParser)
        bases = manual_analysis_parser.__class__.__bases__
        self.assertEqual(correct_bases, bases)

    def test_deduce_pipeline(self):
        self.assertEqual(self.complete_analysis.pipeline, "Ngs")
        self.assertEqual(self.manual_analysis.pipeline, "Manual")


class TestMetric(TestCase):
    """Test custom methods belonging to the metric model."""

    def setUp(self):
        self.project_name = "PT000"
        self.project_path = join(settings.TEST_DIRECTORY, self.project_name)
        self.project = Project.objects.create(
                name=self.project_name, path=self.project_path,
                study_type=settings.STUDY_TYPE_CANCER)
        self.analysis_name = "Ngs.2_5_2"
        self.analysis = Analysis.objects.create(name=self.analysis_name,
                                                project=self.project)
        self.name = "PT000.PT000_Normal.clean.dedup.recal.insert.pdf"
        self.static_file = join(settings.STATIC_ROOT,
                                settings.STATIC_METRIC_LOCATION,
                                self.project_name,
                                self.analysis_name,
                                self.name
                                )

    def test_static_path(self):
        """Test metric static path creation and deletion."""
        self.assertFalse(exists(self.static_file))
        metric = Metric.objects.create(name=self.name, project=self.project,
                                       analysis=self.analysis)
        self.assertEqual(metric.static_path, self.static_file)
        self.assertTrue(exists(self.static_file))
        metric.delete()
        self.assertFalse(exists(self.static_file))
