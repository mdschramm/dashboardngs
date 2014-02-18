from django.conf.urls import patterns, include, url
from .views import (project_list, project_detail,
        project_info_form, project_directory_info_form,
        project_detail_json, pathology_toggle_form,
        new_project_form, existing_project_form, gene_form)

urlpatterns = patterns('',
    url(r"^$", project_list, name="project_list"),
    url(r"^detail/(\w+)/$", project_detail, name="project_detail"),
    url(r"^detail/(\w+)/json/$", project_detail_json,
            name="project_detail_json"),
    url(r"^detail/(\w+)-edit/$", project_info_form,
            name="project_info_form"),
    url(r"^detail/(\w+)-edit-directory/$", project_directory_info_form,
            name="project_directory_info_form"),
    url(r"^detail/(\w+)-pathology-toggle/$", pathology_toggle_form,
            name="pathology_toggle_form"),
    url(r"^new-project-form/$", new_project_form, name="new_project_form"),
    url(r"^existing-project-form/$", existing_project_form,
            name="existing_project_form"),
    url(r"^gene-form/$", gene_form, {"project_name":""}, name="gene_form"),
    url(r"^gene-form/(\w+)/$", gene_form, name="gene_form"),
    #url(r"^makefile-form/$", makefile_form, name="makefile_form"),
    #url(r"^makefile-submitted/$", makefile_submitted,
    #        name="makefile_submitted"),
)
