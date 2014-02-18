from django import forms
from apps.uploads.forms import UploadForm


class CommentForm(UploadForm):
    comment = forms.CharField(widget=forms.Textarea)
    upload = forms.FileField(required=False, help_text="(optional)")

    # This is an ugly hack. By excluding upload and re-adding
    # it above, we are essentially making the field optional while
    # keeping the form validation code from the superclass. -MM
    class Meta(UploadForm.Meta):
        exclude = ('upload',)


class DeleteForm(forms.Form):
    pass
