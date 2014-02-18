from django import forms
from django.forms import ModelForm
from .models import Upload

from os.path import splitext


_accepted_extensions = (
    '.txt',
    '.pdf',
    '.vcf',
    '.jpg',
    '.png',
    '.gif',
    '.html',
    '.htm',
    '.doc',
    '.docx',
    '.rtf',
    '.rst',
    '.md',
)


class UploadForm(ModelForm):
    class Meta:
        model = Upload


    def clean_upload(self):
        upload = self.cleaned_data['upload']
        # These next two lines look unnecessary, but they're not:
        # certain classes inherit from UploadForm and make the upload
        # field optional. Running splitext() on None generates an
        # error, so we need to return before we get to that line.
        # Sorry for being so tricky. -MM
        if not upload:
            return upload
        name, ext = splitext(upload.name)
        if not ext in _accepted_extensions:
            msg = ("Cannot upload because '{0}' files are not accepted by "
                   "this system.".format(ext))
            raise forms.ValidationError(msg)
        return upload


class DeleteForm(forms.Form):
    pass
