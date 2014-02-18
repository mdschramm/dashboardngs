from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from ..models import Project
import os


class ViewsTest(TestCase):
    fixtures = ["analysis_auth.json", "analysis_data.json"]

    def setUp(self):
        self.core_client = Client()
        self.core_client.login(username="core_user", password="password")
        self.ovarian_client = Client()
        self.ovarian_client.login(username="ovarian_user", password="password")
        self.personalized_client = Client()
        self.personalized_client.login(
                username="personalized_user", password="password"
        )
        for project in Project.objects.all():
            project.add_to_profiles()

    def __test_status_codes(self, url, core_code=200, ovarian_code=200,
                            personalized_code=200):
        """
        Test that different users receive appropriate status codes when
        visiting the url.

        """
        self.core_response = self.core_client.get(url)
        self.ovarian_response = self.ovarian_client.get(url)
        self.personalized_response = self.personalized_client.get(url)
        self.assertEqual(self.core_response.status_code, core_code)
        self.assertEqual(self.ovarian_response.status_code, ovarian_code)
        self.assertEqual(self.personalized_response.status_code,
                         personalized_code)

    def test_project_list(self):
        """
        Test the project list view.

        """
        url = os.path.join('/', settings.UGLY_PREFIX, 'analysis/')
        self.__test_status_codes(url, 403, 200, 200)
        # Test that the ovarian user only sees "PT" projects
        self.assertTrue("projects" in self.ovarian_response.context)
        ovarian_projects = self.ovarian_response.context["projects"]
        self.assertTrue(ovarian_projects.count())
        for project in ovarian_projects:
            self.assertTrue(project.name.startswith("PT"))
        # Test that the personalized user sees everything but "PT" projects
        self.assertTrue("projects" in self.personalized_response.context)
        personalized_projects = self.personalized_response.context["projects"]
        self.assertTrue(personalized_projects.count())
        for project in personalized_projects:
            self.assertFalse(project.name.startswith("PT"))

    def test_project_detail(self):
        """
        Test the project detail view.

        Untested:

        * fine-grained permissions, such as view results tables and
          edit pathology toggle
        * results tables won't show up at all, because extra results
          databases won't show up in test database
        * anything to do with colors in the pizza tracker

        """
        url = os.path.join('/', settings.UGLY_PREFIX, 'analysis/detail/LA/')
        self.__test_status_codes(url, 403, 403, 200)
        url = os.path.join('/', settings.UGLY_PREFIX, 'analysis/detail/PT208/')
        self.__test_status_codes(url, 403, 200, 403)
        url = os.path.join('/', settings.UGLY_PREFIX, 'analysis/detail/???/')
        self.__test_status_codes(url, 404, 404, 404)
