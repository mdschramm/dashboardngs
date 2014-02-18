from django import template

register = template.Library()

@register.inclusion_tag("analysis/sidebar.html", takes_context=True)
def sidebar(context):
    user = context["user"]
    try:
        current_project_name = context["project.name"]
    except KeyError:
        current_project_name = ""
    projects = user.get_profile().projects.all().extra(order_by=["-name"])
    return {"projects":projects, "current_project_name":current_project_name}
