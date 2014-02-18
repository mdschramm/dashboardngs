from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..templatetags.projects_tags import navbar, sidebar
from ..models import Project, Study

from os.path import join

class TestTemplateTags(TestCase):
    def setUp(self):
        self.name = "PT000"
        self.path = join(settings.TEST_DIRECTORY, self.name)
        self.project = Project.objects.create(name=self.name, path=self.path)
        self.ovarian_study = Study.objects.create(name="Ovarian")
        self.project.studies.add(self.ovarian_study)

        self.user = User.objects.create_user("test", "test@test.com", "test")
        self.user.get_profile().studies.add(self.ovarian_study)
        self.client.login(username="test", password="test")

    def test_navbar(self):
        context = {"user": self.user}
        context = navbar(context)
        self.assertTrue("study_list" in context)
        study_list = context["study_list"]
        self.assertTrue(self.ovarian_study in study_list)

    def test_sidebar(self):
        context = {"project": self.project}
        context = sidebar(context)
        self.assertTrue("study_list" in context)
        study_list = context["study_list"]
        self.assertTrue(self.ovarian_study in study_list)

        context = {"study": self.ovarian_study}
        context = sidebar(context)
        self.assertTrue("study_list" in context)
        study_list = context["study_list"]
        self.assertTrue(self.ovarian_study in study_list)

    def test_analysis_summary(self):
        """TODO"""
        pass
