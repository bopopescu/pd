# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'PDReport.last_run'
        db.alter_column('metrics_pdreport', 'last_run', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'PDMetric.when'
        db.alter_column('metrics_pdmetric', 'when', self.gf('django.db.models.fields.DateTimeField')())


    def backwards(self, orm):
        
        # Changing field 'PDReport.last_run'
        db.alter_column('metrics_pdreport', 'last_run', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'PDMetric.when'
        db.alter_column('metrics_pdmetric', 'when', self.gf('django.db.models.fields.DateField')())


    models = {
        'metrics.pdmetric': {
            'Meta': {'object_name': 'PDMetric'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': "orm['metrics.PDReport']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {})
        },
        'metrics.pdreport': {
            'Meta': {'object_name': 'PDReport'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['metrics']
