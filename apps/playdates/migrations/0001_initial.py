# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PlaydateInviteDesign'
        db.create_table('playdates_playdateinvitedesign', (
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('small_image', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
            ('big_image', self.gf('django.db.models.fields.URLField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('playdates', ['PlaydateInviteDesign'])

        # Adding model 'Playdate'
        db.create_table('playdates_playdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organizer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('organizer_child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Child'])),
            ('is_dropoff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('activity', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('max_participants', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('expire_option', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('min_participants', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('invite_design', self.gf('django.db.models.fields.related.ForeignKey')(default='Basic', to=orm['playdates.PlaydateInviteDesign'])),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('when_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('when_until', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('playdates', ['Playdate'])

        # Adding unique constraint on 'Playdate', fields ['organizer_child', 'when_from', 'when_until']
        db.create_unique('playdates_playdate', ['organizer_child_id', 'when_from', 'when_until'])

        # Adding model 'PlaydateInviteEmail'
        db.create_table('playdates_playdateinviteemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='1', max_length=1)),
            ('response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('playdate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='email_invites', to=orm['playdates.Playdate'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, db_index=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('playdates', ['PlaydateInviteEmail'])

        # Adding unique constraint on 'PlaydateInviteEmail', fields ['playdate', 'email']
        db.create_unique('playdates_playdateinviteemail', ['playdate_id', 'email'])

        # Adding model 'PlaydateInviteUser'
        db.create_table('playdates_playdateinviteuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='1', max_length=1)),
            ('response', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('playdate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='user_invites', to=orm['playdates.Playdate'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('to_child', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['profiles.Child'])),
        ))
        db.send_create_signal('playdates', ['PlaydateInviteUser'])

        # Adding unique constraint on 'PlaydateInviteUser', fields ['playdate', 'to_child']
        db.create_unique('playdates_playdateinviteuser', ['playdate_id', 'to_child_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PlaydateInviteUser', fields ['playdate', 'to_child']
        db.delete_unique('playdates_playdateinviteuser', ['playdate_id', 'to_child_id'])

        # Removing unique constraint on 'PlaydateInviteEmail', fields ['playdate', 'email']
        db.delete_unique('playdates_playdateinviteemail', ['playdate_id', 'email'])

        # Removing unique constraint on 'Playdate', fields ['organizer_child', 'when_from', 'when_until']
        db.delete_unique('playdates_playdate', ['organizer_child_id', 'when_from', 'when_until'])

        # Deleting model 'PlaydateInviteDesign'
        db.delete_table('playdates_playdateinvitedesign')

        # Deleting model 'Playdate'
        db.delete_table('playdates_playdate')

        # Deleting model 'PlaydateInviteEmail'
        db.delete_table('playdates_playdateinviteemail')

        # Deleting model 'PlaydateInviteUser'
        db.delete_table('playdates_playdateinviteuser')


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
        'playdates.playdate': {
            'Meta': {'unique_together': "(('organizer_child', 'when_from', 'when_until'),)", 'object_name': 'Playdate'},
            'activity': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {}),
            'attending_user_children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'playdates'", 'symmetrical': 'False', 'through': "orm['playdates.PlaydateInviteUser']", 'to': "orm['profiles.Child']"}),
            'expire_option': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invite_design': ('django.db.models.fields.related.ForeignKey', [], {'default': "'Basic'", 'to': "orm['playdates.PlaydateInviteDesign']"}),
            'is_dropoff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_participants': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'min_participants': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'organizer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'organizer_child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Child']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'when_from': ('django.db.models.fields.DateTimeField', [], {}),
            'when_until': ('django.db.models.fields.DateTimeField', [], {})
        },
        'playdates.playdateinvitedesign': {
            'Meta': {'object_name': 'PlaydateInviteDesign'},
            'big_image': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'small_image': ('django.db.models.fields.URLField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'})
        },
        'playdates.playdateinviteemail': {
            'Meta': {'unique_together': "(('playdate', 'email'),)", 'object_name': 'PlaydateInviteEmail'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'playdate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'email_invites'", 'to': "orm['playdates.Playdate']"}),
            'response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'playdates.playdateinviteuser': {
            'Meta': {'unique_together': "(('playdate', 'to_child'),)", 'object_name': 'PlaydateInviteUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'playdate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_invites'", 'to': "orm['playdates.Playdate']"}),
            'response': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1'}),
            'to_child': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profiles.Child']"}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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

    complete_apps = ['playdates']
