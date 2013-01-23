from friends.models import ContactEmail
from django.db import IntegrityError
from emailconfirmation.models import EmailAddress
from mydebug import *

class BasePersistance(object):
    def persist(self, contact, status, credentials):
        if status is None:
            status = self.default_status()
        return self.persist_contact(contact, status, credentials)
    
    def persist_contact(self, contact, status, credentials):
        return status


class ModelPersistance(BasePersistance):
    
    def persist_contact(self, contact, status, credentials):

        obj = created = email_address = user = None
        email = contact["email"]
            
        email = email.lower()
        try:
            email_address = EmailAddress.objects.get(email = email)
            user = email_address.user
        except EmailAddress.DoesNotExist:
            pass

        try:
            obj, created = ContactEmail.objects.get_or_create(
                owner = credentials["user"],
                email = email,
                name = contact["name"],
                user = user,
                import_job = credentials["import_id"]
            )
        except IntegrityError:
            pass

        if "send_invites" in credentials and credentials["send_invites"]:
            if created:
                if user is None:
                    tolog("sending invite")
                    obj.send_invite()
            
        status["total"] += 1
        
        if created:
            status["imported"] += 1
        return status


class InMemoryPersistance(BasePersistance):
    
    def persist_contact(self, contact, status, credentials):
        # @@@ no longer works (need to conform to status contract which could
        # be done by adding a new key or emulating a dict and store contacts
        # that way)
        return status

def mycallback(request, selected):
        return True

