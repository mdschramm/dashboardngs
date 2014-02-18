from django.conf import settings
from django.test import TestCase
from apps.analysis.toolkit import dna_parse
import os


class DNAParseTest(TestCase):
    """
    The test1 directory is completely empty.

    The test2 directory represents a directory in-progress. The patient
    is PID123, and it uses a differently-named results directory.

    The test3 directory represents a completed directory. The patient is
    PT000. There are multiple XML files in this directory, so some
    functions will correctly throw exceptions unless an individual
    XML file is specified.
    """

    def setUp(self):
        self.test1 = os.path.join(settings.TEST_DIRECTORY, "test1")
        self.test2 = os.path.join(settings.TEST_DIRECTORY, "test2")
        self.test3 = os.path.join(settings.TEST_DIRECTORY, "test3")

    def test_find_xml_file(self):
        self.assertIsNone(dna_parse.find_xml_file(self.test1))
        self.assertEqual(dna_parse.find_xml_file(self.test2), "PID123.xml")
        try:
            dna_parse.find_xml_file(self.test3)
        except dna_parse.MultipleXMLFilesFoundException:
            pass
        else:
            self.assertTrue(False)

    def test_find_makefile(self):
        self.assertIsNone(dna_parse.find_makefile(self.test1))
        self.assertEqual(dna_parse.find_makefile(self.test2), "Makefile")
        self.assertEqual(dna_parse.find_makefile(self.test3), "makefile")

    def test_find_results_directory(self):
        test2_makefile = dna_parse.find_makefile(self.test2)
        test3_makefile = dna_parse.find_makefile(self.test3)
        self.assertEqual(dna_parse.find_results_directory(self.test2,
            test2_makefile), "fancy_dir")
        self.assertEqual(dna_parse.find_results_directory(self.test3,
            test3_makefile), "results")
        try:
            dna_parse.find_results_directory(self.test2, "Not a file")
        except IOError:
            pass
        else:
            self.assertTrue(False)

    def test_get_project_name(self):
        test2_makefile = dna_parse.find_makefile(self.test2)
        test3_makefile = dna_parse.find_makefile(self.test3)
        self.assertEqual(dna_parse.get_project_name(self.test2,
                test2_makefile), "PID123")
        try:
            dna_parse.get_project_name(self.test3, test3_makefile)
        except dna_parse.ProjectNameNotInMakefileException:
            pass
        else:
            self.assertTrue(False)
        try:
            dna_parse.get_project_name(self.test2, "Not a file")
        except IOError:
            pass
        else:
            self.assertTrue(False)

    def test_get_sample_names(self):
        test2_xml_file = dna_parse.find_xml_file(self.test2)
        test3_xml_file_1 = "too_many_xml_files1.xml"
        test3_xml_file_2 = "too_many_xml_files2.xml"
        test3_xml_file_3 = "too_many_xml_files3.xml"
        self.assertEqual(dna_parse.get_sample_names(self.test2,
                test2_xml_file), ["PID123_Normal", "PID123_Tumor"])
        self.assertEqual(dna_parse.get_sample_names(self.test3,
                test3_xml_file_1), ["PT000_Tumor", "PT000_Normal"])
        self.assertEqual(dna_parse.get_sample_names(self.test3,
                test3_xml_file_3), [])
        try:
            dna_parse.get_sample_names(self.test3, test3_xml_file_2)
        except dna_parse.ImproperlyFormattedXMLFileException:
            pass
        else:
            self.assertTrue(False)

    def test_is_done(self):
        test2_makefile = dna_parse.find_makefile(self.test2)
        test3_makefile = dna_parse.find_makefile(self.test3)
        test2_results_dir = os.path.join(self.test2,
                dna_parse.find_results_directory(self.test2, test2_makefile))
        test3_results_dir = os.path.join(self.test3,
                dna_parse.find_results_directory(self.test3, test3_makefile))
        self.assertFalse(dna_parse.is_bam_done(test2_results_dir, "PID123"))
        self.assertFalse(dna_parse.is_metric_done(test2_results_dir, "PID123"))
        self.assertFalse(dna_parse.is_vcf_done(test2_results_dir, "PID123"))
        self.assertTrue(dna_parse.is_bam_done(test3_results_dir, "PT000"))
        self.assertTrue(dna_parse.is_metric_done(test3_results_dir, "PT000"))
        self.assertTrue(dna_parse.is_vcf_done(test3_results_dir, "PT000"))

    def test_get_status(self):
        test2_makefile = dna_parse.find_makefile(self.test2)
        test3_makefile = dna_parse.find_makefile(self.test3)
        test2_results_dir = os.path.join(self.test2,
                dna_parse.find_results_directory(self.test2, test2_makefile))
        test3_results_dir = os.path.join(self.test3,
                dna_parse.find_results_directory(self.test3, test3_makefile))
        # Test 2
        self.assertEqual(dna_parse.get_bam_status(test2_results_dir,
                "PID123", "PID123_Normal"), "De-duped, not yet recalibrated.")
        self.assertEqual(dna_parse.get_bam_status(test2_results_dir,
                "PID123", "PID123_Tumor"), "De-duped, not yet recalibrated.")
        self.assertEqual(dna_parse.get_metric_status(test2_results_dir,
                "PID123", "PID123_Normal"), "Cleaned, not yet de-duped.")
        self.assertEqual(dna_parse.get_metric_status(test2_results_dir,
                "PID123", "PID123_Tumor"), "Cleaned, not yet de-duped.")
        self.assertEqual(dna_parse.get_vcf_status(test2_results_dir,
                "PID123", "PID123_Tumor"), "Not done.")
        self.assertEqual(dna_parse.get_project_vcf_status(test2_results_dir,
                "PID123"), "Not done.")
        # Test 3
        self.assertEqual(dna_parse.get_bam_status(test3_results_dir,
                "PT000", "PT000_Normal"), "Done.")
        self.assertEqual(dna_parse.get_bam_status(test3_results_dir,
                "PT000", "PT000_Tumor"), "Done.")
        self.assertEqual(dna_parse.get_metric_status(test3_results_dir,
                "PT000", "PT000_Normal"), "Done.")
        self.assertEqual(dna_parse.get_metric_status(test3_results_dir,
                "PT000", "PT000_Tumor"), "Done.")
        self.assertEqual(dna_parse.get_vcf_status(test3_results_dir,
                "PT000", "PT000_Tumor"), "Done.")
        self.assertEqual(dna_parse.get_project_vcf_status(test3_results_dir,
                "PT000"), "Done.")

    def test_get(self):
        test3_makefile = dna_parse.find_makefile(self.test3)
        test3_results_dir = os.path.join(self.test3,
                dna_parse.find_results_directory(self.test3, test3_makefile))
        bams = {
            "PT000_Normal":"PT000.PT000_Normal.clean.dedup.recal.bam",
            "PT000_Tumor":"PT000.PT000_Tumor.clean.dedup.recal.bam"
        }
        metrics = {
            "PT000":[],
            "samples": {
                "PT000_Normal":
                        ["PT000.PT000_Normal.clean.dedup.recal.insert.pdf"],
                "PT000_Tumor":
                        ["PT000.PT000_Tumor.clean.dedup.recal.insert.pdf"]
            }
        }
        vcfs = {
            "PT000":["PT000.PT000.varscan.vcf"],
            "samples": {
                "PT000_Normal": [],
                "PT000_Tumor": ["PT000.PT000_Tumor.varscan.vcf"]
            }
        }
        self.assertEqual(dna_parse.get_bams(test3_results_dir,
                "PT000", ["PT000_Normal", "PT000_Tumor"]), bams)
        self.assertEqual(dna_parse.get_metrics(test3_results_dir,
                "PT000", ["PT000_Normal", "PT000_Tumor"]), metrics)
        self.assertEqual(dna_parse.get_vcfs(test3_results_dir,
                "PT000", ["PT000_Normal", "PT000_Tumor"]), vcfs)
