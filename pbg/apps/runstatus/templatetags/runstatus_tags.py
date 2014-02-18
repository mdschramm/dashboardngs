from django import template

register = template.Library()

@register.inclusion_tag("runstatus/sidebar.html", takes_context=True)
def sidebar(context):
    try:
        current_machine = context["machine"]
    except KeyError:
        current_machine = ""
    machines = ["Amee", "corey", "Hal", "Sid", "zoe"]
    return {"current_machine":current_machine, "machines":machines}
