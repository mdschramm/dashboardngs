from django import template
from ..toolkit.parse import NGSMixin

register = template.Library()

@register.inclusion_tag("projects/navbar.html", takes_context=True)
def navbar(context):
    user = context["user"]
    context["study_list"] = user.get_profile().studies.all()
    return context


@register.inclusion_tag("projects/sidebar.html", takes_context=True)
def sidebar(context):
    # Code for project detail
    if "project" in context:
        project = context["project"]
        context["study_list"] = project.studies.all()
    # Code for project list
    elif "study" in context:
        context["study_list"] = [context["study"]]
    return context


def _get_ngs_status_information(status):
    statuses = {
            str(NGSMixin.DONE): ("Done", "success"),
            str(NGSMixin.DEDUPED): ("Deduped", "warning"),
            str(NGSMixin.CLEANED): ("Cleaned", "warning"),
            str(NGSMixin.NOT_DONE): ("Not done", "danger")
            }
    try:
        return statuses[str(status)]
    except KeyError:
        return ("Unknown", "active")


@register.inclusion_tag("projects/analysis_summary.html")
def analysis_summary(analysis):
    parser = analysis.get_parser()
    context = {
            "analysis": analysis,
            "parser": parser
            }
    if analysis.pipeline == "Ngs":
        context["show_progress"] = True
        context["results_files"] = ["BAMs", "QCs", "VCFs"]
        statuses = [parser.get_bam_status(),
                    parser.get_metric_status(),
                    parser.get_vcf_status()
                    ]
        context["status_list"] = [
                _get_ngs_status_information(status) for status in statuses
                ]
    context["sample_list"] = analysis.samples.all()
    return context

