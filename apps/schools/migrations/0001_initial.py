# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'School'
        db.create_table('schools_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gsid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=15, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=2, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('lon', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('pd', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('schools', ['School'])

        # Adding model 'Zip_School_Prox'
        db.create_table('schools_zip_school_prox', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip', self.gf('django.db.models.fields.related.ForeignKey')(related_name='school_prox', to=orm['places.Zip'])),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['schools.School'])),
            ('dst', self.gf('django.db.models.fields.CharField')(max_length=5)),
        ))
        db.send_create_signal('schools', ['Zip_School_Prox'])

        # Adding unique constraint on 'Zip_School_Prox', fields ['zip', 'school']
        db.create_unique('schools_zip_school_prox', ['zip_id', 'school_id'])

        # Adding model 'PD_School'
        db.create_table('schools_pd_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal('schools', ['PD_School'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Zip_School_Prox', fields ['zip', 'school']
        db.delete_unique('schools_zip_school_prox', ['zip_id', 'school_id'])

        # Deleting model 'School'
        db.delete_table('schools_school')

        # Deleting model 'Zip_School_Prox'
        db.delete_table('schools_zip_school_prox')

        # Deleting model 'PD_School'
        db.delete_table('schools_pd_school')


    models = {
        'places.zip': {
            'Meta': {'object_name': 'Zip'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'state_full': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10', 'db_index': 'True'})
        },
        'schools.pd_school': {
            'Meta': {'object_name': 'PD_School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'schools.school': {
            'Meta': {'object_name': 'School'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'gsid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '15', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'pd': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'})
        },
        'schools.zip_school_prox': {
            'Meta': {'unique_together': "(('zip', 'school'),)", 'object_name': 'Zip_School_Prox'},
            'dst': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['schools.School']"}),
            'zip': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'school_prox'", 'to': "orm['places.Zip']"})
        }
    }

    complete_apps = ['schools']
