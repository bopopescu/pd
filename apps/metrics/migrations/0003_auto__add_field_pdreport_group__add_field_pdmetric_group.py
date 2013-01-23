# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'PDReport.group'
        db.add_column('metrics_pdreport', 'group', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'PDMetric.group'
        db.add_column('metrics_pdmetric', 'group', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'PDReport.group'
        db.delete_column('metrics_pdreport', 'group')

        # Deleting field 'PDMetric.group'
        db.delete_column('metrics_pdmetric', 'group')


    models = {
        'metrics.pdmetric': {
            'Meta': {'object_name': 'PDMetric'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metrics'", 'to': "orm['metrics.PDReport']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {})
        },
        'metrics.pdreport': {
            'Meta': {'object_name': 'PDReport'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_run': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['metrics']
