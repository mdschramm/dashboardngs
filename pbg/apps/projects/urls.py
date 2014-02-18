from django.conf.urls import patterns, include, url

from .views import (StudyListView, ProjectListView, ProjectDetailView,
                    AnalysisDetailView)

urlpatterns = (
    url(
        regex=r"^$",
        view=StudyListView.as_view(),
        name="study_list"
    ),
    url(
        regex=r"^study/(?P<study>\w+)/$",
        view=ProjectListView.as_view(),
        name="project_list"
    ),
    url(
        regex=r"^detail/(?P<project>[-_\w]+)/$",
        view=ProjectDetailView.as_view(),
        name="project_detail"
    ),
    url(
        regex=r"^detail/([-\w]+)/([-.\w]+)/$",
        view=AnalysisDetailView.as_view(),
        name="analysis_detail"
    ),
    url(
        r"^cancer/",
        include("apps.cancer.urls", namespace="cancer")
    ),
)
