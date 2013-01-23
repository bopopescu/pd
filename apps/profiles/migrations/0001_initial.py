# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Profile'
        db.create_table('profiles_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('li_profile', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('fb_profile', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('tw_profile', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('profiles', ['Profile'])

        # Adding model 'FacebookUser'
        db.create_table('profiles_facebookuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fbuser', unique=True, to=orm['auth.User'])),
            ('facebook_id', self.gf('django.db.models.fields.CharField')(max_length=150, db_index=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal('profiles', ['FacebookUser'])

        # Adding model 'Child'
        db.create_table('profiles_child', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('birthdate', self.gf('django.db.models.fields.DateField')()),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['schools.School'], null=True)),
            ('anon_prof_privacy', self.gf('django.db.models.fields.CharField')(default='public', max_length=10)),
            ('basic_prof_privacy', self.gf('django.db.models.fields.CharField')(default='second', max_length=10)),
            ('ext_prof_privacy', self.gf('django.db.models.fields.CharField')(default='playlist', max_length=10)),
            ('playlist_privacy', self.gf('django.db.models.fields.CharField')(default='playlist', max_length=10)),
            ('photo_privacy', self.gf('django.db.models.fields.CharField')(default='playlist', max_length=10)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('playdate_requirements', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('diet', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('snacks', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('characters', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('toys', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('languages', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('sports', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('activities', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('grade_level', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('teacher', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('profiles', ['Child'])

        # Adding model 'Adult_Child'
        db.create_table('profiles_adult_child', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('adult', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attached_children', to=orm['auth.User'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attached_adults', to=orm['profiles.Child'])),
            ('relation', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('can_edit_profile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_view_schedule', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_edit_schedule', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_view_playlist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_edit_playlist', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_view_photos', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('can_upload_photos', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('access_role', self.gf('django.db.models.fields.CharField')(default='admin', max_length=10)),
            ('can_display_child', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('profiles', ['Adult_Child'])

        # Adding model 'Friendship'
        db.create_table('profiles_friendship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='are_friends', to=orm['profiles.Child'])),
            ('to_child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['profiles.Child'])),
            ('added', self.gf('django.db.models.fields.DateField')(default=datetime.date.today)),
        ))
        db.send_create_signal('profiles', ['Friendship'])

        # Adding unique constraint on 'Friendship', fields ['from_child', 'to_child']
        db.create_unique('profiles_friendship', ['from_child_id', 'to_child_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Friendship', fields ['from_child', 'to_child']
        db.delete_unique('profiles_friendship', ['from_child_id', 'to_child_id'])

        # Deleting model 'Profile'
        db.delete_table('profiles_profile')

        # Deleting model 'FacebookUser'
        db.delete_table('profiles_facebookuser')

        # Deleting model 'Child'
        db.delete_table('profiles_child')

        # Deleting model 'Adult_Child'
        db.delete_table('profiles_adult_child')

        # Deleting model 'Friendship'
        db.delete_table('profiles_friendship')


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
        'profiles.adult_child': {
            'Meta': {'object_name': 'Adult_Child'},
            'access_role': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '10'}),
            'adult': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attached_children'", 'to': "orm['auth.User']"}),
            'can_display_child': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_playlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_profile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_edit_schedule': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_upload_photos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_view_photos': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_view_playlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'can_view_schedule': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attached_adults'", 'to': "orm['profiles.Child']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        'profiles.child': {
            'Meta': {'object_name': 'Child'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'activities': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'adults': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'children'", 'symmetrical': 'False', 'through': "orm['profiles.Adult_Child']", 'to': "orm['auth.User']"}),
            'anon_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '10'}),
            'basic_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'second'", 'max_length': '10'}),
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'characters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'diet': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ext_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Child']", 'through': "orm['profiles.Friendship']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'grade_level': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'photo_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'playdate_requirements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'playlist_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schools.School']", 'null': 'True'}),
            'snacks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sports': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'toys': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'profiles.facebookuser': {
            'Meta': {'object_name': 'FacebookUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fbuser'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'profiles.friendship': {
            'Meta': {'unique_together': "(('from_child', 'to_child'),)", 'object_name': 'Friendship'},
            'added': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'from_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'are_friends'", 'to': "orm['profiles.Child']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['profiles.Child']"})
        },
        'profiles.profile': {
            'Meta': {'object_name': 'Profile'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fb_profile': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'li_profile': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'tw_profile': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        'schools.school': {
            'Meta': {'object_name': 'School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['profiles']
