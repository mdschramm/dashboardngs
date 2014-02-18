from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadForm, DeleteForm
from .models import Upload, UploadContainer


def upload(request, content_type_id, object_id, description):
    content_type = ContentType.objects.get_for_id(content_type_id)
    parent = content_type.get_object_for_this_type(pk=object_id)
    back_url = parent.get_absolute_url()
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = request.FILES['upload']
            try:
                uploads = UploadContainer.objects.get(\
                        content_type__pk=content_type_id,
                        object_id=object_id,
                        description=description)
            except UploadContainer.DoesNotExist:
                uploads = UploadContainer.objects.create(\
                        parent=parent,
                        description=description)
            Upload.objects.create(upload=upload, container=uploads,
                    user=request.user.get_profile())
            return HttpResponseRedirect(back_url)
    else:
        form = UploadForm()
    context = {}
    context["form"] = form
    context["back_url"] = back_url
    return render(request, 'uploads/form.html', context)


def delete(request, upload_id):
    upload = Upload.objects.get(pk=upload_id)
    parent = upload.container.parent
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            upload.delete()
            return HttpResponseRedirect(parent.get_absolute_url())
    else:
        form = DeleteForm()
    context = {}
    context['form'] = form
    context['upload'] = upload
    context["back_url"] = parent.get_absolute_url()
    return render(request, 'uploads/confirm_delete.html', context)
