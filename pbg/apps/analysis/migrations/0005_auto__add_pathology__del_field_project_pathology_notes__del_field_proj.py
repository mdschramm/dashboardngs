# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Pathology'
        db.create_table('analysis_pathology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('flavor', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'])),
        ))
        db.send_create_signal('analysis', ['Pathology'])

        # Deleting field 'Project.pathology_notes'
        db.delete_column('analysis_project', 'pathology_notes')

        # Deleting field 'Project.sequencing_notes'
        db.delete_column('analysis_project', 'sequencing_notes')

        # Deleting field 'Project.fastq_notes'
        db.delete_column('analysis_project', 'fastq_notes')

        # Deleting field 'Project.vcf_notes'
        db.delete_column('analysis_project', 'vcf_notes')

        # Deleting field 'Project.bam_notes'
        db.delete_column('analysis_project', 'bam_notes')

        # Deleting field 'Project.metric_notes'
        db.delete_column('analysis_project', 'metric_notes')

        # Deleting field 'Sample.pathology_wes'
        db.delete_column('analysis_sample', 'pathology_wes')

        # Deleting field 'Sample.pathology_wgs'
        db.delete_column('analysis_sample', 'pathology_wgs')

        # Deleting field 'Sample.pathology_rna'
        db.delete_column('analysis_sample', 'pathology_rna')

        # Adding field 'BAM.sample'
        db.add_column('analysis_bam', 'sample',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Pathology'
        db.delete_table('analysis_pathology')

        # Adding field 'Project.pathology_notes'
        db.add_column('analysis_project', 'pathology_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Project.sequencing_notes'
        db.add_column('analysis_project', 'sequencing_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Project.fastq_notes'
        db.add_column('analysis_project', 'fastq_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Project.vcf_notes'
        db.add_column('analysis_project', 'vcf_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Project.bam_notes'
        db.add_column('analysis_project', 'bam_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Project.metric_notes'
        db.add_column('analysis_project', 'metric_notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Sample.pathology_wes'
        db.add_column('analysis_sample', 'pathology_wes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Sample.pathology_wgs'
        db.add_column('analysis_sample', 'pathology_wgs',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Sample.pathology_rna'
        db.add_column('analysis_sample', 'pathology_rna',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'BAM.sample'
        db.delete_column('analysis_bam', 'sample_id')


    models = {
        'analysis.bam': {
            'Meta': {'object_name': 'BAM'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Project']"}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Sample']", 'null': 'True', 'blank': 'True'})
        },
        'analysis.metric': {
            'Meta': {'object_name': 'Metric'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Project']"}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Sample']", 'null': 'True', 'blank': 'True'})
        },
        'analysis.pathology': {
            'Meta': {'object_name': 'Pathology'},
            'flavor': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Sample']"}),
            'value': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'analysis.project': {
            'Meta': {'object_name': 'Project'},
            'blog_bam': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_bam'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'blog_fastq': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_fastq'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'blog_metric': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_metric'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'blog_pathology': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_pathology'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'blog_sequencing': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_sequencing'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'blog_vcf': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'blog_vcf'", 'unique': 'True', 'null': 'True', 'to': "orm['comments.Blog']"}),
            'cancer_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'results_directory': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'rna': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {}),
            'wes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wgs': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'analysis.sample': {
            'Meta': {'object_name': 'Sample'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Project']"}),
            'rin_score': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'}),
            'rna_metrics_found': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tissue_of_origin': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'tumor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tumor_class': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'tumor_purity': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '2', 'blank': 'True'}),
            'tumor_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'analysis.sequencinginfo': {
            'Meta': {'object_name': 'SequencingInfo'},
            'flavor': ('django.db.models.fields.CharField', [], {'max_length': '16', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'run_status_sample': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['runstatus.Sample']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Sample']"})
        },
        'analysis.vcf': {
            'Meta': {'object_name': 'VCF'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Project']"})
        },
        'comments.blog': {
            'Meta': {'object_name': 'Blog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'runstatus.project': {
            'Meta': {'object_name': 'Project'},
            'fastq_ready': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sample_sheet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['runstatus.SampleSheet']"})
        },
        'runstatus.run': {
            'Meta': {'object_name': 'Run'},
            'current_cycle': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'run_directory': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'run_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'total_cycles': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'runstatus.sample': {
            'Meta': {'object_name': 'Sample'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lanes': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '32'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['runstatus.Project']"}),
            'reads': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        },
        'runstatus.samplesheet': {
            'Meta': {'object_name': 'SampleSheet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['runstatus.Run']"})
        }
    }

    complete_apps = ['analysis']