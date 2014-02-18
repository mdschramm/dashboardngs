from django.contrib import admin

from .models import (Project, Sample, Pathology, SequencingInfo, BAM,
        Metric, VCF)

admin.site.register(Project)
admin.site.register(Sample)
admin.site.register(Pathology)
admin.site.register(SequencingInfo)
admin.site.register(BAM)
admin.site.register(Metric)
admin.site.register(VCF)
