from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, RedirectView

from .models import Project, Study, Analysis


class StudyListView(ListView):
    model = Study
    context_object_name = "study_list"

    def get_queryset(self):
        return self.request.user.get_profile().studies.all()


class ProjectListView(ListView):
    model = Project
    context_object_name = "project_list"

    def get_queryset(self):
        """
        Return the project list only if it's from a study the user can view.

        """
        study_name = self.kwargs["study"]
        study = get_object_or_404(Study, name=study_name)
        if not study in self.request.user.get_profile().studies.all():
            raise PermissionDenied
        return study.project_set.all()

    def get_context_data(self, **kwargs):
        context_data = super(ProjectListView, self).get_context_data(**kwargs)
        context_data["study_name"] = self.kwargs["study"]
        return context_data


class ProjectDetailView(DetailView):
    model = Project
    slug_field = "name"
    slug_url_kwarg = "project"

    def get_object(self):
        """Return the project only if it's in a study the user can view."""
        project = super(ProjectDetailView, self).get_object()
        project_studies = set(study for study in project.studies.all())
        user_studies = set(study for study in
                self.request.user.get_profile().studies.all())
        intersection = project_studies & user_studies
        if not intersection:
            raise PermissionDenied
        return project


class AnalysisDetailView(RedirectView):
    """Redirects analysis to study-specific analysis."""
    permanent = False

    def get_redirect_url(self):
        project_name = self.args[0]
        analysis_name = self.args[1]
        analysis = Analysis.objects.get(name=analysis_name,
                                        project__name=project_name)
        study_type = analysis.project.study_type
        # This shouldn't break as long as all study types are namespaces,
        # which is the exact definition of a study type
        reverse_namespace = "projects:{0}:analysis_detail".format(study_type)
        return reverse(reverse_namespace, args=(project_name, analysis_name))
