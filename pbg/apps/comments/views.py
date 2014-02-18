from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import CommentForm, DeleteForm
from .models import Comment, CommentContainer
from apps.uploads.models import Upload, UploadContainer


def view(request, content_type_id, object_id, description):
    content_type = ContentType.objects.get_for_id(content_type_id)
    parent = content_type.get_object_for_this_type(pk=object_id)
    back_url = parent.get_absolute_url()
    context = {}
    context["content_type_id"] = content_type_id
    context["object_id"] = object_id
    context["description"] = description
    context["back_url"] = back_url
    try:
        container = CommentContainer.objects.get(\
                content_type__pk=content_type_id,
                object_id=object_id,
                description=description)
    except CommentContainer.DoesNotExist:
        context["comments"] = []
    else:
        context["comments"] = container.comment_set.all()
    return render(request, "comments/view.html", context)


def post(request, content_type_id, object_id, description):
    content_type = ContentType.objects.get_for_id(content_type_id)
    parent = content_type.get_object_for_this_type(pk=object_id)
    back_url = reverse("comments:view", args=(content_type_id,
            object_id, description))
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                comment_container = CommentContainer.objects.get(\
                        content_type__pk=content_type_id,
                        object_id=object_id,
                        description=description)
            except CommentContainer.DoesNotExist:
                comment_container = CommentContainer.objects.create(\
                        parent=parent,
                        description=description)
            comment = Comment.objects.create(comment=cd["comment"],
                    container=comment_container,
                    user=request.user.get_profile())
            if cd["upload"]:
                upload = request.FILES['upload']
                upload_container = UploadContainer.objects.create(
                        parent=comment,
                        description="comment"
                        )
                Upload.objects.create(upload=upload,
                        container=upload_container,
                        user=request.user.get_profile()
                        )
            return HttpResponseRedirect(back_url)
    else:
        form = CommentForm()
    context = {}
    context["form"] = form
    context["back_url"] = back_url
    return render(request, 'comments/post.html', context)


def delete(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    back_url = comment.container.get_absolute_url()
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            comment.delete()
            return HttpResponseRedirect(back_url)
    else:
        form = DeleteForm()
    context = {}
    context["form"] = form
    context["comment"] = comment
    context["back_url"] = back_url
    return render(request, 'comments/confirm_delete.html', context)
