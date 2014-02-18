from django.views.generic import DetailView

from .models import CancerAnalysis

class AnalysisDetailView(DetailView):
    model = CancerAnalysis
    template_name = "cancer/analysis_detail.html"
    context_object_name = "analysis"

    def get_object(self):
        project_name = self.args[0]
        analysis_name = self.args[1]
        return CancerAnalysis.objects.get(name=analysis_name,
                                          project__name=project_name)

    def get_context_data(self, **kwargs):
        context_data = super(AnalysisDetailView, self).get_context_data(
                **kwargs)
        context_data["annol_results"] = True
        return context_data
