from django.db import models
from apps.projects.models import Sample, Analysis, BAM, Metric, VCF


class CancerSample(Sample):
    """A CancerSample contains extra fields not in vanilla Sample."""
    tissue_of_origin = models.CharField(max_length=255, blank=True)
    tumor = models.BooleanField()
    tumor_purity = models.DecimalField(blank=True, null=True,
                                       max_digits=3, decimal_places=2)


class CancerAnalysis(Analysis):
    """
    The CancerAnalysis model contains cancer-aware sync_with_directory()
    methods.
    """
    class Meta:
        proxy = True

    def sync_with_directory(self):
        """TODO: add RNA pipeline hook."""
        if self.pipeline == "Ngs":
            self.__sync_with_ngs_directory()

    def __sync_with_ngs_directory(self):
        """Syncs with an NGS pipeline results directory."""
        parser = self.get_parser()
        samples = parser.get_xml_info()

        # Create samples.
        for sample_name, sample_info in samples.items():
            sample, created = CancerSample.objects.get_or_create(
                    name=sample_name, project=self.project,
                    tumor=sample_info["tumor"], 
                    tumor_purity=sample_info["purity"]
                    )
            if not sample in self.samples.all():
                self.samples.add(sample)

        def find_associated_sample(results_file_name):
            """
            Helper function to see if a sample is associated with
            the results file.

            """
            elements = results_file_name.split(".")
            for sample in self.samples.all():
                if sample.name in elements:
                    return sample
            return None

        def delete_if_not_in_filesystem(fs_query_set, query_set):
            not_in_filesystem = set(query_set) - set(fs_query_set)
            for obj in not_in_filesystem:
                obj.delete()

        # Create BAMs.
        bams = parser.get_bams()
        bam_list = [
            (BAM.objects.get_or_create(
                    name=bam, project=self.project, analysis=self,
                    sample=find_associated_sample(bam)))[0]
            for bam in bams
            ]
        # Delete extra BAMs.
        delete_if_not_in_filesystem(bam_list,
                                    BAM.objects.filter(analysis=self))

        # Create Metrics.
        metrics = parser.get_metrics()
        metric_list = [
            (Metric.objects.get_or_create(
                    name=metric, project=self.project, analysis=self,
                    sample=find_associated_sample(metric)))[0]
            for metric in metrics
            ]
        # Delete extra Metrics.
        delete_if_not_in_filesystem(metric_list,
                                    Metric.objects.filter(analysis=self))

        # Create VCFs.
        vcfs = parser.get_vcfs()
        vcf_list = [
            (VCF.objects.get_or_create(
                    name=vcf, project=self.project, analysis=self,
                    sample=find_associated_sample(vcf)))[0]
            for vcf in vcfs
            ]
        # Delete extra VCFs.
        delete_if_not_in_filesystem(vcf_list,
                                    VCF.objects.filter(analysis=self))
