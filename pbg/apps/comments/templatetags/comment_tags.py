from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import CommentContainer

register = template.Library()

@register.inclusion_tag("comments/comment.html")
def comment(parent, description):
    content_type = ContentType.objects.get_for_model(parent)
    try:
        container = CommentContainer.objects.get(\
                content_type__pk=content_type.pk,
                object_id=parent.pk,
                description=description)
    except CommentContainer.DoesNotExist:
        count = 0
    else:
        count = container.num_entries
    return {"content_type_id":content_type.pk,
            "object_id":parent.pk,
            "description":description,
            "count":count}
