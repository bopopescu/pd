# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FriendSuggestion'
        db.create_table('friends_friendsuggestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='suggested_friends', to=orm['profiles.Child'])),
            ('suggested_child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['profiles.Child'])),
            ('why', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('friends', ['FriendSuggestion'])


    def backwards(self, orm):
        
        # Deleting model 'FriendSuggestion'
        db.delete_table('friends_friendsuggestion')


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
        'comments.comment': {
            'Meta': {'ordering': "['-added']", 'object_name': 'Comment'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['auth.User']"}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'friends.contactemail': {
            'Meta': {'unique_together': "(('owner', 'email'),)", 'object_name': 'ContactEmail'},
            'added': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contactemail'", 'to': "orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contactemail_user'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'friends.contactfb': {
            'Meta': {'unique_together': "(('owner', 'facebook_id'),)", 'object_name': 'ContactFB'},
            'added': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'facebook_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contactfb'", 'to': "orm['auth.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contactfb_user'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'friends.friendshipinvitation': {
            'Meta': {'unique_together': "(('from_child', 'to_child'),)", 'object_name': 'FriendshipInvitation'},
            'from_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_from_child'", 'to': "orm['profiles.Child']"}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_from_user'", 'to': "orm['auth.User']"}),
            'how_related': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'sent': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'to_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_to_child'", 'to': "orm['profiles.Child']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invitations_to_user'", 'to': "orm['auth.User']"})
        },
        'friends.friendsuggestion': {
            'Meta': {'object_name': 'FriendSuggestion'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'suggested_friends'", 'to': "orm['profiles.Child']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'suggested_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['profiles.Child']"}),
            'why': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'friends.googletoken': {
            'Meta': {'object_name': 'GoogleToken'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'token': ('django.db.models.fields.TextField', [], {}),
            'token_secret': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'googletokens'", 'to': "orm['auth.User']"})
        },
        'friends.joininvitationemail': {
            'Meta': {'ordering': "['-sent']", 'object_name': 'JoinInvitationEmail'},
            'confirmation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['friends.ContactEmail']"}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'join_from'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'sent': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'photos.album': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Album'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'albums'", 'null': 'True', 'to': "orm['auth.User']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '101'})
        },
        'photos.photo': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Photo'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photos'", 'to': "orm['photos.Album']"}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '201'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
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
            'album': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['photos.Album']"}),
            'anon_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'public'", 'max_length': '10'}),
            'basic_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'birthdate': ('django.db.models.fields.DateField', [], {}),
            'characters': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'diet': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'ext_prof_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'first_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'friends': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['profiles.Child']", 'through': "orm['profiles.Friendship']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'grade_level': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['photos.Photo']", 'null': 'True', 'blank': 'True'}),
            'photo_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'playdate_requirements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'playlist_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'schedule_privacy': ('django.db.models.fields.CharField', [], {'default': "'playlist'", 'max_length': '10'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['schools.School']", 'null': 'True'}),
            'snacks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sports': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'toys': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'profiles.friendship': {
            'Meta': {'unique_together': "(('from_child', 'to_child'),)", 'object_name': 'Friendship'},
            'added': ('django.db.models.fields.DateField', [], {'default': 'datetime.date.today'}),
            'from_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'are_friends'", 'to': "orm['profiles.Child']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': "orm['profiles.Child']"})
        },
        'schools.school': {
            'Meta': {'object_name': 'School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['friends']
