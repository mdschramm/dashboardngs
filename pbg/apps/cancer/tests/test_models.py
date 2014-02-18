from django.conf import settings
from django.test import TestCase

from apps.projects.models import (Study, Project, Analysis, Sample, BAM,
                                  Metric, VCF)
from os.path import exists, join
from os import unlink


class TestCancerAnalysis(TestCase):
    """Test custom methods belonging to the Analysis model."""

    def setUp(self):
        self.project_name = "PT000"
        self.project_path = join(settings.TEST_DIRECTORY, self.project_name)
        self.project = Project.objects.create(name=self.project_name,
                                              path=self.project_path,
                                              study_type="cancer")
        self.complete_analysis_name = "Ngs.2_5_2"
        self.incomplete_analysis_name = "Ngs.2_5_2.mutectOnly"


        self.complete_analysis = Analysis.objects.create(
                name=self.complete_analysis_name, project=self.project)
        self.incomplete_analysis = Analysis.objects.create(
                name=self.incomplete_analysis_name, project=self.project)
        parser = self.complete_analysis.get_parser()
        file_name = "tmp.vcf"
        self.temp_vcf_path = join(parser.results_dir_path, file_name)

    def tearDown(self):
        """Remove symlinks so that TestMetric's symlink tests work."""
        for metric in Metric.objects.all():
            metric.remove_static_path()
        if exists(self.temp_vcf_path):
            unlink(self.temp_vcf_path)

    def test_sync_with_directory(self):
        """
        Test if sync_with_directory adds BAMs, Metrics, and VCFs.

        """

        # Test when BAMs, Metrics, and VCFs are present
        complete = self.complete_analysis
        complete.sync_with_directory()
        self.assertTrue(Sample.objects.filter(analysis=complete).count())
        self.assertTrue(BAM.objects.filter(analysis=complete).count())
        self.assertTrue(Metric.objects.filter(analysis=complete).count())
        self.assertTrue(VCF.objects.filter(analysis=complete).count())

        # Test sample name generation
        correct_sample_names = ["PT000_Normal", "PT000_Tumor"]
        sample_names = sorted(
                [sample.name for sample in complete.samples.all()]
                )
        self.assertEqual(correct_sample_names, sample_names)

        # Test sample assignment
        for bam in BAM.objects.filter(analysis=complete):
            self.assertIsNotNone(bam.sample)

        # Test in an (almost) empty directory
        incomplete = self.incomplete_analysis
        incomplete.sync_with_directory()
        self.assertTrue(Sample.objects.filter(analysis=incomplete).count())
        self.assertFalse(BAM.objects.filter(analysis=incomplete).count())
        self.assertFalse(Metric.objects.filter(analysis=incomplete).count())
        self.assertFalse(VCF.objects.filter(analysis=incomplete).count())

    def test_sync_with_directory_additions_and_deletions(self):
        """Test sync_with_directory when adding or deleting files."""
        analysis = self.complete_analysis

        # Test basic sync with directory
        analysis.sync_with_directory()
        self.assertEqual(BAM.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(Metric.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(VCF.objects.filter(analysis=analysis).count(), 2)

        # Add a new file
        with open(self.temp_vcf_path, "w") as f:
            pass
        analysis.sync_with_directory()
        self.assertEqual(BAM.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(Metric.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(VCF.objects.filter(analysis=analysis).count(), 3)

        # Remove the file
        unlink(self.temp_vcf_path)
        analysis.sync_with_directory()
        self.assertEqual(BAM.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(Metric.objects.filter(analysis=analysis).count(), 2)
        self.assertEqual(VCF.objects.filter(analysis=analysis).count(), 2)
