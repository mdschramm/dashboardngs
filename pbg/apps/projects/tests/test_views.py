from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Study, Project, Metric

from os.path import join

class ViewsTest(TestCase):
    def setUp(self):
        self.name1 = "PT000"
        self.path1 = join(settings.TEST_DIRECTORY, self.name1)
        self.project1 = Project.objects.create(
                name=self.name1, path=self.path1,
                study_type=settings.STUDY_TYPE_CANCER)
        self.name2 = "PT001"
        self.path2 = join(settings.TEST_DIRECTORY, self.name2)
        self.project2 = Project.objects.create(name=self.name2,
                                               path=self.path2)
        self.ovarian_study = Study.objects.create(name="Ovarian")
        self.personalized_study = Study.objects.create(name="Personalized")
        self.project1.studies.add(self.ovarian_study)
        self.project2.studies.add(self.personalized_study)

        self.project1.sync_with_directory(deep=False) # add analyses

        self.user = User.objects.create_user("test", "test@test.com", "test")
        self.user.get_profile().studies.add(self.ovarian_study)
        self.client.login(username="test", password="test")

    def tearDown(self):
        """Not used, actually. Just here as a failsafe."""
        for metric in Metric.objects.all():
            metric.remove_static_path()

    def test_study_list(self):
        """Test study list limited to a certain user."""
        response = self.client.get(reverse("projects:study_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("study_list" in response.context)
        self.assertEqual(response.context["study_list"].count(), 1)
        self.assertEqual(response.context["study_list"][0],
                         self.ovarian_study)

    def test_project_list(self):
        """Test project list view limited to a certain study."""

        # Test correct functionality when user has permission
        response = self.client.get(reverse("projects:project_list",
                                           kwargs={"study": "Ovarian"}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("study_list" in response.context)
        self.assertTrue("project_list" in response.context)
        projects = response.context["project_list"]
        self.assertEqual(projects.count(), 1)
        self.assertEqual(projects[0], self.project1)

        # Test 403 error when user does not have permission
        response = self.client.get(reverse("projects:project_list",
                                           kwargs={"study": "Personalized"}))
        self.assertEqual(response.status_code, 403)

    def test_project_detail(self):
        """Test basic functionality of project detail view."""

        # Test correct functionality when user has permission
        response = self.client.get(reverse("projects:project_detail",
                                           kwargs={"project": "PT000"}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("study_list" in response.context)
        self.assertTrue("project" in response.context)
        self.assertEqual(response.context["project"], self.project1)

        # Test 403 error when user does not have permission
        response = self.client.get(reverse("projects:project_detail",
                                           kwargs={"project": "PT001"}))
        self.assertEqual(response.status_code, 403)

    def test_analysis_detail_redirect(self):
        """Test redirect functionality of analysis detail."""
        response = self.client.get(reverse("projects:analysis_detail",
                                           args=(self.project1.name,
                                                 "Ngs.2_5_2")))
        self.assertEqual(response.status_code, 302)

