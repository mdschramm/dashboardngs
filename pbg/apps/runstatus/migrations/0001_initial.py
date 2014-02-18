# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Run'
        db.create_table('runstatus_run', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('run_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('run_directory', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('current_cycle', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_cycles', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('runstatus', ['Run'])

        # Adding model 'SampleSheet'
        db.create_table('runstatus_samplesheet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['runstatus.Run'])),
        ))
        db.send_create_signal('runstatus', ['SampleSheet'])

        # Adding model 'Project'
        db.create_table('runstatus_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('sample_sheet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['runstatus.SampleSheet'])),
            ('fastq_ready', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('runstatus', ['Project'])

        # Adding model 'Sample'
        db.create_table('runstatus_sample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['runstatus.Project'])),
            ('reads', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('lanes', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=32)),
        ))
        db.send_create_signal('runstatus', ['Sample'])


    def backwards(self, orm):
        # Deleting model 'Run'
        db.delete_table('runstatus_run')

        # Deleting model 'SampleSheet'
        db.delete_table('runstatus_samplesheet')

        # Deleting model 'Project'
        db.delete_table('runstatus_project')

        # Deleting model 'Sample'
        db.delete_table('runstatus_sample')


    models = {
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

    complete_apps = ['runstatus']