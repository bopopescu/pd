# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'WaitingList'
        db.create_table('splash_waitinglist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, db_index=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('signup_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('splash', ['WaitingList'])


    def backwards(self, orm):
        
        # Deleting model 'WaitingList'
        db.delete_table('splash_waitinglist')


    models = {
        'splash.waitinglist': {
            'Meta': {'object_name': 'WaitingList'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['splash']
