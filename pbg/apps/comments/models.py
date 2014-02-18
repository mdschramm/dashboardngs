from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse


class CommentContainer(models.Model):
    description = models.CharField(max_length=256, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    parent = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.content_type.app_label + " " + \
               self.content_type.name + " " + \
               self.parent.__unicode__() + " " + \
               self.description

    def get_absolute_url(self):
        return reverse("comments:view", args=(self.content_type.pk,
            self.object_id, self.description))

    def num_entries(self):
        return self.comment_set.count()



class Comment(models.Model):
    user = models.ForeignKey('core.UserProfile', editable=False, blank=True,
            null=True)
    container = models.ForeignKey(CommentContainer, editable=False)
    time = models.DateTimeField(auto_now=True)
    comment = models.TextField()

    def __unicode__(self):
        return self.user.user.username + " " + unicode(self.time)

    def get_absolute_url(self):
        return self.container.get_absolute_url()


@receiver(models.signals.post_delete, sender=Comment)
def comment_delete(sender, instance, **kwargs):
    if instance.container:
        qs = instance.container.comment_set.all()
        if not qs:
            instance.container.delete()


@receiver(models.signals.post_delete)
def parent_of_comment_delete(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    object_id = instance.pk
    if type(object_id) != int:
        return
    comment_containers = CommentContainer.objects.filter(\
            content_type=content_type,
            object_id=object_id)
    for comment_container in comment_containers:
        for comment in comment_container.comment_set.all():
            comment.delete()
