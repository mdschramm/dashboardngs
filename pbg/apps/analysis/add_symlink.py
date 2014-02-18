import sys
import os
sys.path.insert(0, os.path.abspath("../.."))

from apps.analysis.models import Metric

for metric in Metric.objects.all():
    if metric.classification == "rna" or metric.classification == "three_prime":
        metric.create_symlink(rna=True)
    else:
        metric.create_symlink()
