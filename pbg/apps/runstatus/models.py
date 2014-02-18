from django.core.urlresolvers import reverse
from django.db import models


class RunManager(models.Manager):
    def create_from_json(self, machine_name, run_info):
        if not run_info["end"]: # convert empty string to NULL
            end_date = None
        else:
            end_date = run_info["end"]
        run = Run.objects.create(machine_name=machine_name,
                run_number=run_info["runnum"],
                run_directory=run_info["name"],
                start_date=run_info["start"],
                end_date=end_date,
                current_cycle=run_info["curcycle"],
                total_cycles=run_info["cycles"],
                aborted=run_info["aborted"],)
        run.update(run_info)


class Run(models.Model):
    machine_name = models.CharField(max_length=256)
    run_number = models.IntegerField(null=True)
    run_directory = models.CharField(max_length=256)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    current_cycle = models.IntegerField(default=0)
    total_cycles = models.IntegerField(default=0)
    aborted = models.BooleanField()

    objects = RunManager()

    class Meta:
        permissions = (
            ("view_run", "Can view the run status dashboard"),
        )

    def __unicode__(self):
        return self.run_directory

    def get_absolute_url(self):
        return reverse("run_status:run_status", args=(self.machine_name,))

    @property
    def name(self):
        return self.run_directory

    @property
    def sample_sheets(self):
        return self.samplesheet_set.all()

    def update(self, run_info):
        needs_save = False
        if not self.end_date and run_info["end"]:
            self.end_date = run_info["end"]
            needs_save = True
        if not self.run_number and run_info["runnum"]:
            self.run_number = run_info["runnum"]
            needs_save = True
        if not self.aborted and run_info["aborted"]:
            self.aborted = run_info["aborted"]
            needs_save = True
        if self.current_cycle != self.total_cycles:
            self.current_cycle = run_info["curcycle"]
            needs_save = True
        if needs_save:
            self.save()
        for sample_sheet_name, sample_sheet_info in run_info["csvs"].items():
            try:
                sample_sheet = SampleSheet.objects.get(name=sample_sheet_name,
                        run=self)
            except SampleSheet.DoesNotExist:
                sample_sheet = \
                        SampleSheet.objects.create(name=sample_sheet_name,
                        run=self)
            sample_sheet.update(sample_sheet_info)


class SampleSheet(models.Model):
    name = models.CharField(max_length=256)
    run = models.ForeignKey(Run)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.run.get_absolute_url()

    @property
    def projects(self):
        return self.project_set.all()

    def update(self, sample_sheet_info):
        for project_name, project_info in sample_sheet_info.items():
            try:
                project = Project.objects.get(name=project_name,
                        sample_sheet=self)
            except Project.DoesNotExist:
                project = Project.objects.create(name=project_name,
                        sample_sheet=self,
                        fastq_ready=project_info["fastqready"])
            project.update(project_info)


class Project(models.Model):
    name = models.CharField(max_length=256)
    sample_sheet = models.ForeignKey(SampleSheet)
    fastq_ready = models.BooleanField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.sample_sheet.run.get_absolute_url()

    @property
    def samples(self):
        return self.sample_set.all()

    def update(self, project_info):
        if not self.fastq_ready and project_info["fastqready"]:
            self.fastq_ready = True
            self.save()
        for sample_name, sample_info in project_info["samples"].items():
            try:
                sample = Sample.objects.get(name=sample_name, project=self)
            except Sample.DoesNotExist:
                sample = Sample.objects.create(name=sample_name,
                        project=self,
                        reads=sample_info["reads"],
                        lanes=",".join(sample_info["lanes"]))
            sample.update(sample_info)

    
class Sample(models.Model):
    name = models.CharField(max_length=256)
    project = models.ForeignKey(Project)
    reads = models.IntegerField(null=True)
    lanes = models.CommaSeparatedIntegerField(max_length=32)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return self.project.sample_sheet.run.get_absolute_url()

    def update(self, sample_info):
        if not self.reads and sample_info["reads"]:
            self.reads = sample_info["reads"]
            self.save()
