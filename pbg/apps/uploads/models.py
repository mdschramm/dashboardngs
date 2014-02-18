from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import os


class UploadContainer(models.Model):
    description = models.CharField(max_length=256, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    parent = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.content_type.app_label + " " + \
               self.content_type.name + " " + \
               self.parent.__unicode__() + " " + \
               self.description


class Upload(models.Model):
    user = models.ForeignKey('core.UserProfile', editable=False, blank=True,
            null=True)
    container = models.ForeignKey(UploadContainer, blank=True, null=True,
            editable=False)
    # upload path is always model/description/username/filename
    # e.g. project/candidate_gene_info/admin/info.pdf
    upload = models.FileField(
            upload_to=lambda inst, name: os.path.join(
                inst.container.content_type.app_label,
                inst.container.content_type.name,
                str(inst.container.object_id),
                inst.container.description,
                inst.user.user.username,
                name
                )
            )

    def __unicode__(self):
        return self.upload.path

    @property
    def base_name(self):
        return os.path.basename(self.upload.name)


@receiver(models.signals.post_delete, sender=Upload)
def upload_delete(sender, instance, **kwargs):
    if instance.upload:
        if os.path.isfile(instance.upload.path):
            os.remove(instance.upload.path)
    if instance.container:
        qs = instance.container.upload_set.all()
        if not qs:
            instance.container.delete()


@receiver(models.signals.post_delete)
def parent_of_upload_delete(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    object_id = instance.pk
    # These next two lines need some explanation. Here goes:
    # This function is called when ANY object is deleted--including
    # objects that don't necessarily have a primary key that's a
    # positive integer field. Turns out, internally, that value is
    # stored as a long, not an int, so the isinstance test takes a
    # long for that reason.
    if not isinstance(instance.pk, long):
        return
    upload_containers = UploadContainer.objects.filter(
            content_type=content_type, object_id=object_id
            )
    for upload_container in upload_containers:
        for upload in upload_container.upload_set.all():
            upload.delete()
