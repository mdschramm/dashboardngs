from django.conf import settings
from django.test import TestCase

from os.path import join

from ..toolkit.parse import ProjectParser, NGSMixin

class TestProjectParser(TestCase):
    """Test the parsing script for the new directory structure."""

    def setUp(self):
        self.path = join(settings.TEST_DIRECTORY, "PT000")

        # Names of folders in the PT000/Raw directory
        self.dna = "Dna.IlluminaHiSeq2500.Wes.notes"
        self.rna = "Rna.IonPgm.Hotspot_v2"

        # Names of folders in the PT000/Processed directory
        self.ngs = "Ngs.2_5_2"
        self.ngs_mutect = "Ngs.2_5_2.mutectOnly"
        self.manual = "ManualSpecial.2013_08_21"

        # Create the ProjectParser
        self.parser = ProjectParser(self.path)

    def test_get_raw(self):
        """Test the function that lists raw directories."""
        correct_list = [self.dna, self.rna]
        raw_list = self.parser.get_raw()
        raw_list.sort()
        self.assertEqual(correct_list, raw_list)

    def test_get_processed(self):
        """Test the function that lists processed directories."""
        correct_list = [self.manual, self.ngs, self.ngs_mutect]
        processed_list = self.parser.get_processed()
        processed_list.sort()
        self.assertEqual(correct_list, processed_list)

    def test_parse_raw_name(self):
        """Test the static method that parses a raw directory name."""
        correct_output_dna = {
                "library_type": "Dna",
                "platform": "IlluminaHiSeq2500",
                "library_prep": "Wes",
                "notes": "notes"
                }
        correct_output_rna = {
                "library_type": "Rna",
                "platform": "IonPgm",
                "library_prep": "Hotspot_v2",
                "notes": ""
                }
        output_dna = self.parser.parse_raw_name(self.dna)
        output_rna = self.parser.parse_raw_name(self.rna)
        self.assertEqual(correct_output_dna, output_dna)
        self.assertEqual(correct_output_rna, output_rna)

    def test_parse_processed_name(self):
        """Test the static method that parses a processed directory name."""
        correct_ngs = {
                "pipeline_name": "Ngs",
                "version": "2.5.2",
                "notes": ""
                }
        correct_ngs_mutect = {
                "pipeline_name": "Ngs",
                "version": "2.5.2",
                "notes": "mutectOnly"
                }
        correct_manual = {
                "pipeline_name": "Manual",
                "description": "Special",
                "date": "2013_08_21"
                }
        output_ngs = self.parser.parse_processed_name(self.ngs)
        output_ngs_mutect = self.parser.parse_processed_name(self.ngs_mutect)
        output_manual = self.parser.parse_processed_name(self.manual)
        self.assertEqual(correct_ngs, output_ngs)
        self.assertEqual(correct_ngs_mutect, output_ngs_mutect)
        self.assertEqual(correct_manual, output_manual)

class TestGeneralAnalysisMixin(TestCase):
    """Test the general get() functions in the GeneralAnalysisMixin."""

    def setUp(self):
        self.path = join(settings.TEST_DIRECTORY, "PT000")

        self.ngs = "Ngs.2_5_2"
        self.ngs_mutect = "Ngs.2_5_2.mutectOnly"

        class GeneralAnalysisParser(NGSMixin, ProjectParser):
            pass
        self.ngs_parser = GeneralAnalysisParser(path=self.path, name=self.ngs)
        self.ngs_mutect_parser = GeneralAnalysisParser(path=self.path,
                                                       name=self.ngs_mutect)





    def test_get_bams(self):
        """Tests the function that returns a list of BAMs."""

        # Test the full case
        correct_bams = [
            "PT000.PT000_Normal.clean.dedup.recal.bam",
            "PT000.PT000_Tumor.clean.dedup.recal.bam"
        ]
        bams = self.ngs_parser.get_bams()
        bams.sort()
        self.assertEqual(correct_bams, bams)

        # Test the empty case
        self.assertEqual(self.ngs_mutect_parser.get_bams(), [])

    def test_get_metrics(self):
        """Tests the function that returns a list of Metrics."""

        # Test the full case
        correct_metrics = [
            "PT000.PT000_Normal.clean.dedup.recal.insert.pdf",
            "PT000.PT000_Tumor.clean.dedup.recal.insert.pdf"
        ]
        metrics = self.ngs_parser.get_metrics()
        metrics.sort()
        self.assertEqual(correct_metrics, metrics)

        # Test the empty case
        self.assertEqual(self.ngs_mutect_parser.get_metrics(), [])

    def test_get_vcfs(self):
        """Tests the function that returns a list of VCFs."""

        # Test the full case
        correct_vcfs = [
            "PT000.PT000.varscan.vcf",
            "PT000.PT000_Tumor.varscan.vcf"
        ]
        vcfs = self.ngs_parser.get_vcfs()
        vcfs.sort()
        self.assertEqual(correct_vcfs, vcfs)

        # Test the empty case
        self.assertEqual(self.ngs_mutect_parser.get_vcfs(), [])


class TestNGSMixin(TestCase):
    """Test the get status functions from the NGS pipeline."""

    def setUp(self):
        self.path = join(settings.TEST_DIRECTORY, "PT000")

        self.ngs = "Ngs.2_5_2"
        self.ngs_mutect = "Ngs.2_5_2.mutectOnly"
        self.manual = "ManualSpecial.2013_08_21"

        class NGSParser(NGSMixin, ProjectParser):
            pass
        self.ngs_parser = NGSParser(path=self.path, name=self.ngs)
        self.ngs_mutect_parser = NGSParser(path=self.path,
                                           name=self.ngs_mutect)
        self.manual_parser = NGSParser(path=self.path, name=self.manual)

    def test_get_bam_status(self):
        """Test the function that recturns the status of the BAMs."""

        # Test the completed case
        correct_bam_status = NGSMixin.DONE
        bam_status = self.ngs_parser.get_bam_status()
        self.assertEqual(correct_bam_status, bam_status)

        # Test the incomplete case
        correct_mutect_bam_status = NGSMixin.DEDUPED
        mutect_bam_status = self.ngs_mutect_parser.get_bam_status()
        self.assertEqual(correct_mutect_bam_status, mutect_bam_status)

        # Test the nonexistant case
        manual_bam_status = self.manual_parser.get_bam_status()
        self.assertIsNone(manual_bam_status)

    def test_get_metric_status(self):
        """Test the function that recturns the status of the Metrics."""

        # Test the completed case
        correct_metric_status = NGSMixin.DONE
        metric_status = self.ngs_parser.get_metric_status()
        self.assertEqual(correct_metric_status, metric_status)

        # Test the incomplete case
        correct_mutect_metric_status = NGSMixin.CLEANED
        mutect_metric_status = self.ngs_mutect_parser.get_metric_status()
        self.assertEqual(correct_mutect_metric_status, mutect_metric_status)

        # Test the nonexistant case
        manual_metric_status = self.manual_parser.get_metric_status()
        self.assertIsNone(manual_metric_status)

    def test_get_vcf_status(self):
        """Test the function that recturns the status of the VCFs."""

        # Test the completed case
        correct_vcf_status = NGSMixin.DONE
        vcf_status = self.ngs_parser.get_vcf_status()
        self.assertEqual(correct_vcf_status, vcf_status)

        # Test the incomplete case
        correct_mutect_vcf_status = NGSMixin.NOT_DONE
        mutect_vcf_status = self.ngs_mutect_parser.get_vcf_status()
        self.assertEqual(correct_mutect_vcf_status, mutect_vcf_status)

        # Test the nonexistant case
        manual_vcf_status = self.manual_parser.get_vcf_status()
        self.assertIsNone(manual_vcf_status)
