# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('analysis_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('keyword', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('results_directory', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('version', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('cancer_name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wgs', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('wes', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('rna', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('analysis', ['Project'])

        # Adding model 'Sample'
        db.create_table('analysis_sample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Project'])),
            ('tissue_of_origin', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('rin_score', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1, blank=True)),
            ('tumor', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tumor_purity', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=2, blank=True)),
            ('tumor_type', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('tumor_class', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('rna_metrics_found', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('analysis', ['Sample'])

        # Adding model 'Pathology'
        db.create_table('analysis_pathology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('flavor', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'])),
        ))
        db.send_create_signal('analysis', ['Pathology'])

        # Adding model 'SequencingInfo'
        db.create_table('analysis_sequencinginfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'])),
            ('run_status_sample', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['runstatus.Sample'], unique=True, null=True, blank=True)),
            ('flavor', self.gf('django.db.models.fields.CharField')(max_length=16, blank=True)),
        ))
        db.send_create_signal('analysis', ['SequencingInfo'])

        # Adding model 'BAM'
        db.create_table('analysis_bam', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Project'])),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'], null=True, blank=True)),
        ))
        db.send_create_signal('analysis', ['BAM'])

        # Adding model 'Metric'
        db.create_table('analysis_metric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Project'])),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'], null=True, blank=True)),
            ('rna', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('analysis', ['Metric'])

        # Adding model 'VCF'
        db.create_table('analysis_vcf', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Project'])),
            ('sample', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['analysis.Sample'], null=True, blank=True)),
        ))
        db.send_create_signal('analysis', ['VCF'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('analysis_project')

        # Deleting model 'Sample'
        db.delete_table('analysis_sample')

        # Deleting model 'Pathology'
        db.delete_table('analysis_pathology')

        # Deleting model 'SequencingInfo'
        db.delete_table('analysis_sequencinginfo')

        # Deleting model 'BAM'
        db.delete_table('analysis_bam')

        # Deleting model 'Metric'
        db.delete_table('analysis_metric')

        # Deleting model 'VCF'
        db.delete_table('analysis_vcf')


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
            'rna': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'Meta': {'ordering': "['name']", 'object_name': 'Sample'},
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
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Project']"}),
            'sample': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['analysis.Sample']", 'null': 'True', 'blank': 'True'})
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
            'aborted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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