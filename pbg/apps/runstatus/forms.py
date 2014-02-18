from django import forms
from .toolkit.pulljson import get_run_info

class Node2Form(forms.Form):
    """Sends run information back to node2 for further processing."""
    machine_name = forms.ChoiceField(
            choices=(
                ("Amee", "Amee"),
                ("corey", "Corey"),
                ("Hal", "Hal"),
                ("Sid", "Sid"),
                ("zoe", "Zoe"),
                )
            )
    run_directory = forms.CharField(
            max_length=256,
            help_text="Example: 130101_SN12345678_0123_ABCDEFGHIJ"
            )
    run_number = forms.IntegerField()
    sample_sheet = forms.CharField()
    action = forms.CharField()

    def clean(self):
        cleaned_data = super(Node2Form, self).clean()
        json = get_run_info(
                cleaned_data.get("machine_name"),
                cleaned_data.get("run_directory"),
                )
        if not json:
            msg = "The machine/run directory combination does not exist."
            raise forms.ValidationError(msg)
        if json["runnum"] != cleaned_data.get("run_number"):
            msg = "The given run number does not belong to that directory."
            raise forms.ValidationError(msg)
        if cleaned_data.get("sample_sheet") not in json["csvs"]:
            msg = "The given sample sheet cannot be found in that directory."
            raise forms.ValidationError(msg)
        return cleaned_data


class RunAbortedForm(forms.Form):
    pass
