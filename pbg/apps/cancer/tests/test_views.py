from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.projects.models import Study, Project, Analysis

from os.path import join

class ViewsTest(TestCase):
    def setUp(self):
        self.project_name = "PT000"
        self.analysis_name = "Ngs.2_5_2"
        self.path = join(settings.TEST_DIRECTORY, self.project_name)
        self.project = Project.objects.create(
                name=self.project_name, path=self.path,
                study_type=settings.STUDY_TYPE_CANCER)
        self.study = Study.objects.create(name="Ovarian")
        self.project.studies.add(self.study)
        self.analysis = Analysis.objects.create(name=self.analysis_name,
                                                project=self.project)
        self.user = User.objects.create_user("test", "test@test.com", "test")
        self.user.get_profile().studies.add(self.study)
        self.client.login(username="test", password="test")

    def test_analysis_detail(self):
        response = self.client.get(reverse("projects:cancer:analysis_detail",
                                           args=(self.project.name,
                                                 self.analysis.name)))
        self.assertTrue("analysis" in response.context)
        self.assertEqual(response.context["analysis"], self.analysis)
