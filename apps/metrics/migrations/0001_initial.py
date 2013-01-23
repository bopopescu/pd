# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PDReport'
        db.create_table('metrics_pdreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('klass', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_run', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('metrics', ['PDReport'])

        # Adding model 'PDMetric'
        db.create_table('metrics_pdmetric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metrics', to=orm['metrics.PDReport'])),
            ('when', self.gf('django.db.models.fields.DateField')()),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('metrics', ['PDMetric'])


    def backwards(self, orm):
        
        # Deleting model 'PDReport'
        db.delete_table('metrics_pdreport')

        # Deleting model 'PDMetric'
        db.delete_table('metrics_pdmetric')


    models = {
        'metrics.pdmetric': {
            'Meta': {'object_name': 'PDMetric'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': "orm['metrics.PDReport']"}),
            'when': ('django.db.models.fields.DateField', [], {})
        },
        'metrics.pdreport': {
            'Meta': {'object_name': 'PDReport'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_run': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['metrics']
