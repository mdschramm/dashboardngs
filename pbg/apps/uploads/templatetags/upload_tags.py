from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import UploadContainer

register = template.Library()

@register.inclusion_tag("uploads/upload.html")
def upload(parent, description):
    content_type = ContentType.objects.get_for_model(parent)
    return {"content_type_id":content_type.pk,
            "object_id":parent.pk,
            "description":description}


@register.inclusion_tag("uploads/show.html")
def show_uploads(parent, description):
    content_type = ContentType.objects.get_for_model(parent)
    try:
        upload_container = UploadContainer.objects.get(\
                content_type__pk=content_type.pk,
                object_id=parent.pk,
                description=description)
    except UploadContainer.DoesNotExist:
        return {}
    return {"uploads":upload_container.upload_set.all()}
