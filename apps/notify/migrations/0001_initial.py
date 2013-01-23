# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MessagePreference'
        db.create_table('notify_messagepreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('send', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('notify', ['MessagePreference'])

        # Adding unique constraint on 'MessagePreference', fields ['user', 'type', 'medium']
        db.create_unique('notify_messagepreference', ['user_id', 'type', 'medium'])

        # Adding model 'MessagePreferenceDefaults'
        db.create_table('notify_messagepreferencedefaults', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('send', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('notify', ['MessagePreferenceDefaults'])

        # Adding unique constraint on 'MessagePreferenceDefaults', fields ['type', 'medium']
        db.create_unique('notify_messagepreferencedefaults', ['type', 'medium'])

        # Adding model 'UpdateQueueBatch'
        db.create_table('notify_updatequeuebatch', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pickled_data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('notify', ['UpdateQueueBatch'])

        # Adding model 'Update'
        db.create_table('notify_update', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='updates', to=orm['auth.User'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('update_type', self.gf('django.db.models.fields.CharField')(default='general', max_length=10)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('unseen', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('notify', ['Update'])

        # Adding model 'InternalMessage'
        db.create_table('notify_internalmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='received_messages', null=True, to=orm['auth.User'])),
            ('parent_msg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='next_messages', null=True, to=orm['notify.InternalMessage'])),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('replied_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sender_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('recipient_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('notify', ['InternalMessage'])

        # Adding model 'FBPost'
        db.create_table('notify_fbpost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('notify', ['FBPost'])

        # Adding model 'Email'
        db.create_table('notify_email', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('notify', ['Email'])

        # Adding model 'MessageContent'
        db.create_table('notify_messagecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('medium', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('part', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('notify', ['MessageContent'])

        # Adding unique constraint on 'MessageContent', fields ['type', 'medium', 'part']
        db.create_unique('notify_messagecontent', ['type', 'medium', 'part'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'MessageContent', fields ['type', 'medium', 'part']
        db.delete_unique('notify_messagecontent', ['type', 'medium', 'part'])

        # Removing unique constraint on 'MessagePreferenceDefaults', fields ['type', 'medium']
        db.delete_unique('notify_messagepreferencedefaults', ['type', 'medium'])

        # Removing unique constraint on 'MessagePreference', fields ['user', 'type', 'medium']
        db.delete_unique('notify_messagepreference', ['user_id', 'type', 'medium'])

        # Deleting model 'MessagePreference'
        db.delete_table('notify_messagepreference')

        # Deleting model 'MessagePreferenceDefaults'
        db.delete_table('notify_messagepreferencedefaults')

        # Deleting model 'UpdateQueueBatch'
        db.delete_table('notify_updatequeuebatch')

        # Deleting model 'Update'
        db.delete_table('notify_update')

        # Deleting model 'InternalMessage'
        db.delete_table('notify_internalmessage')

        # Deleting model 'FBPost'
        db.delete_table('notify_fbpost')

        # Deleting model 'Email'
        db.delete_table('notify_email')

        # Deleting model 'MessageContent'
        db.delete_table('notify_messagecontent')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'notify.email': {
            'Meta': {'object_name': 'Email'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'notify.fbpost': {
            'Meta': {'object_name': 'FBPost'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'notify.internalmessage': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'InternalMessage'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': "orm['notify.InternalMessage']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': "orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        'notify.messagecontent': {
            'Meta': {'unique_together': "(('type', 'medium', 'part'),)", 'object_name': 'MessageContent'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'part': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'notify.messagepreference': {
            'Meta': {'unique_together': "(('user', 'type', 'medium'),)", 'object_name': 'MessagePreference'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'notify.messagepreferencedefaults': {
            'Meta': {'unique_together': "(('type', 'medium'),)", 'object_name': 'MessagePreferenceDefaults'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medium': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'send': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'notify.update': {
            'Meta': {'ordering': "['-added']", 'object_name': 'Update'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'unseen': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'update_type': ('django.db.models.fields.CharField', [], {'default': "'general'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updates'", 'to': "orm['auth.User']"})
        },
        'notify.updatequeuebatch': {
            'Meta': {'object_name': 'UpdateQueueBatch'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickled_data': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['notify']
