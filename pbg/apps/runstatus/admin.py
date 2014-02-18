from django.contrib import admin

from .models import Run, SampleSheet, Project, Sample

admin.site.register(Run)
admin.site.register(SampleSheet)
admin.site.register(Project)
admin.site.register(Sample)

