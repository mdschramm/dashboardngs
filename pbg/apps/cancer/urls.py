from django.conf.urls import patterns, include, url

from .views import AnalysisDetailView

urlpatterns = (
    url(
        regex=r"^detail/([-\w]+)/([-.\w]+)/$",
        view=AnalysisDetailView.as_view(),
        name="analysis_detail"
    ),
)
