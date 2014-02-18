from django.conf import settings
from django.test import TestCase
from apps.projects.toolkit.parse import ProjectParser, NGSMixin
from ..toolkit.parse import CancerMixin

from os.path import join

class TestCancerResultsFinder(TestCase):

    def setUp(self):
        self.project_name = "PT000"
        self.path = join(settings.TEST_DIRECTORY, self.project_name)
        self.ngs_dir = "Ngs.2_5_2"
        class CancerParser(CancerMixin, NGSMixin, ProjectParser):
            pass
        self.parser = CancerParser(path=self.path, name=self.ngs_dir)

    def test_get_xml_info(self):
        xml_info = self.parser.get_xml_info()

        correct_sample_names = ["PT000_Normal", "PT000_Tumor"]
        sample_names = sorted([sample_name for sample_name in xml_info])
        self.assertEqual(correct_sample_names, sample_names)

        correct_tumor_purity = 0.52
        tumor_purity = xml_info["PT000_Tumor"]["purity"]
        self.assertEqual(correct_tumor_purity, tumor_purity)

        self.assertTrue(xml_info["PT000_Tumor"]["tumor"])
        self.assertFalse(xml_info["PT000_Normal"]["tumor"])
        self.assertIsNone(xml_info["PT000_Normal"]["purity"])
