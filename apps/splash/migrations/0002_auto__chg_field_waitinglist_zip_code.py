# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'WaitingList.zip_code'
        db.alter_column('splash_waitinglist', 'zip_code', self.gf('django.db.models.fields.CharField')(max_length=7))


    def backwards(self, orm):
        
        # Changing field 'WaitingList.zip_code'
        db.alter_column('splash_waitinglist', 'zip_code', self.gf('django.db.models.fields.CharField')(max_length=5))


    models = {
        'splash.waitinglist': {
            'Meta': {'object_name': 'WaitingList'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '7'})
        }
    }

    complete_apps = ['splash']
