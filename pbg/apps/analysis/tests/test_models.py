from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from apps.analysis.models import (Project, Sample, Pathology, SequencingInfo,
        BAM, Metric, VCF)
from apps.analysis.toolkit import dna_parse
import os


class ModelManagerTest(TestCase):
    def setUp(self):
        self.project1 = Project.objects.create(name="test1", path="/test1/",
                results_directory="results", version="1", wgs=True)
        self.project2 = Project.objects.create(name="test2", path="/test2/",
                results_directory="results", version="1", wgs=True,
                wes=True, rna=True)
        self.project3a = Project.objects.create(name="test3", path="/test3/",
                results_directory="results", version="1", wes=True,
                rna=True)
        self.project3b = Project.objects.create(name="test3", path="/test3/",
                results_directory="results2", version="2", wes=True,
                rna=True)
        self.user = User.objects.create_user('testuser',
                'mark.micchelli@mssm.edu', 'password')
        self.admin = User.objects.create_user('testadmin',
                'mark.micchelli@mssm.edu', 'password')
        self.admin.is_staff = True
        self.admin.save()
        self.path = os.path.join(settings.TEST_DIRECTORY, "test3")

    def test_versions(self):
        """Test new and current version functions."""
        self.assertEqual(Project.objects.current_version("test3"), 2)
        self.assertEqual(Project.objects.next_version("test3"), 3)
        self.assertEqual(Project.objects.current_version("dne"), 0)
        self.assertEqual(Project.objects.next_version("dne"), 1)

    def test_custom_get(self):
        """Test custom get_project function that uses versioning."""
        project = Project.objects.get(name="test3")
        self.assertEqual(project.version, 2)
        project = Project.objects.get(name="test3", version="1")
        self.assertEqual(project.version, 1)
        try:
            project = Project.objects.get(name="test4", version="1")
        except Project.DoesNotExist:
            pass
        else:
            self.assertTrue(False)
        try:
            project = Project.objects.get(results_directory="results")
        except Project.MultipleObjectsReturned:
            pass
        else:
            self.assertTrue(False)

    def test_create_new(self):
        project = Project.objects.create_new("test_project", self.user)
        self.assertTrue(project in self.user.get_profile().projects.all())
        self.assertTrue(project in self.admin.get_profile().projects.all())

    def test_create_existing(self):
        project = Project.objects.create_existing(self.path, self.user,
                makefile="good_makefile", xml_file="too_many_xml_files1.xml")
        self.assertTrue(project)
        self.assertTrue(project in self.user.get_profile().projects.all())
        self.assertTrue(project in self.admin.get_profile().projects.all())
        samples = Sample.objects.filter(project=project)
        self.assertEqual(samples.count(), 2) # PT000_Normal and PT000_Tumor
        project.update_progress()
        bams = BAM.objects.filter(project=project)
        self.assertTrue(bams.count())
        metrics = Metric.objects.filter(project=project)
        self.assertTrue(metrics.count())
        vcfs = VCF.objects.filter(project=project)
        self.assertTrue(vcfs.count())


class MetricCopyTest(TestCase):
    def setUp(self):
        self.path = os.path.join(settings.TEST_DIRECTORY, "test3/")

    def test_create_dna_from_project(self):
        project = Project.objects.create(name="PT000", version=1,
                path=self.path, results_directory="results")
        Sample.objects.create(name="PT000_Normal", project=project)
        Sample.objects.create(name="PT000_Tumor", project=project, tumor=True)
        metrics = Metric.objects.create_dna_from_project(project)
        self.assertTrue(metrics)
        metric_names = [metric.name for metric in metrics]
        self.assertEqual(set(metric_names),
                set(("PT000.PT000_Normal.clean.dedup.recal.insert.pdf",
                    "PT000.PT000_Tumor.clean.dedup.recal.insert.pdf")))
        metric1_path = os.path.join(settings.STATIC_ROOT,
                "metrics/", str(project.pk), "PT000_Normal",
                "PT000.PT000_Normal.clean.dedup.recal.insert.pdf")
        metric2_path = os.path.join(settings.STATIC_ROOT,
                "metrics/", str(project.pk), "PT000_Tumor",
                "PT000.PT000_Tumor.clean.dedup.recal.insert.pdf")
        self.assertTrue(os.path.exists(metric1_path))
        self.assertTrue(os.path.exists(metric2_path))
        project.delete()
        self.assertFalse(os.path.exists(metric1_path))
        self.assertFalse(os.path.exists(metric2_path))
