import authority
from authority import permissions
from models import Child, Adult_Child
from django.contrib.auth.models import User
from Cheetah.Templates._SkeletonPage import True


class UserPermission(permissions.BasePermission):
    label = 'user_permission'
    checks = ('view_profile',)

    def can_view_user_profile(self, child):
        if self.user in child.adults:
            return True

        return False


class ChildPermission(permissions.BasePermission):
    label = 'child_permission'
    checks = ('can_edit_child_schedule',
              'can_view_child_schedule',
              'can_edit_child_playlist',
              'can_view_child_playlist',
              'can_edit_child_profile',
              'can_view_child_anonymous_profile',
              'can_view_child_basic_profile',
              'can_view_child_extended_profile',
              'can_display_child_on_profile',
              'can_view_child_photos',
              'can_upload_child_photos',
              )

    last_child = None
    cached_ac = None

    def has_private_access(self, child):
        return False

    def is_in_playlist(self, child):
        if self.user.get_profile().is_child_in_network(child):
            return True        
        return False
    
    def is_in_second(self, child):
        if self.user.get_profile().is_child_in_second_network(child):
            return True        
        return False      
    
    def is_public(self, child):
        if self.user.is_authenticated():
            return True
        return False

    def has_required_access(self, child, required_access):
        if required_access == 'private':
            return self.has_private_access(child)
        elif required_access == 'playlist':
            return self.is_in_playlist(child)
        elif required_access == 'second':
            return (self.is_in_playlist(child) or self.is_in_second(child))
        else:
            # make sure playdation user?
            return self.is_public(child)


    def get_ac(self, child):
        if self.last_child is not None:
            if self.last_child == child:
                return self.cached_ac
        try:
            ac = Adult_Child.objects.get(adult=self.user, child=child)
            self.cached_ac = ac
            self.last_child = child
            return ac
        except Adult_Child.DoesNotExist:
            self.cached_ac = None            
            self.last_child = None
            return None

# just checks whether child is in ac for this parent
    def is_child_mine(self, child):
        ac = self.get_ac(child)
        if ac:
            return True
        
        return False


    def can_edit_child_schedule(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_edit_schedule
        
        return False

    def can_upload_child_photos(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_upload_photos
        
        return False

    def can_edit_child_playlist(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_edit_playlist
        
        return False

    def can_edit_child_profile(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_edit_profile
        
        return False

    def can_display_child_on_profile(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_display_child
        
        return False

# ---------------
# view permissions - can depend on network connection
# ---------------

    def can_view_child_schedule(self, child):
        ac = self.get_ac(child)
        if ac:
            if ac.can_view_schedule:
                return True

        required_access = child.ext_prof_privacy
        
        if self.has_required_access(child, required_access):
            return True
        
        return False


    def can_view_child_photos(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_view_photos

        required_access = child.photo_privacy
        
        if self.has_required_access(child, required_access):
            return True
        
        return False


    def can_view_child_playlist(self, child):
        ac = self.get_ac(child)
        if ac:
            return ac.can_view_playlist

        required_access = child.playlist_privacy
        
        if self.has_required_access(child, required_access):
            return True

        
        return False

    def can_view_child_anon_profile(self, child):
        ac = self.get_ac(child)
        if ac:
            return True

        required_access = child.anon_prof_privacy
        
        if self.has_required_access(child, required_access):
            return True
        
        return False


    def can_view_child_basic_profile(self, child):
        ac = self.get_ac(child)
        if ac:
            return True

        required_access = child.basic_prof_privacy
        
        if self.has_required_access(child, required_access):
            return True
        
        return False



    def can_view_child_extended_profile(self, child):
        ac = self.get_ac(child)
        if ac:
            return True

        required_access = child.ext_prof_privacy
        
        if self.has_required_access(child, required_access):
            return True
        
        return False





authority.register(Child, ChildPermission)
authority.register(User, UserPermission)
