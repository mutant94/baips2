from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Message(models.Model):
    content = models.CharField(max_length=255)
    owner = models.ForeignKey(User)
    editor = models.ForeignKey(User, related_name='editor_user', blank=True, null=True)

    def can_content_be_edited_by(self, user):
        if self.editor:
            return self.owner.id == user.id or self.editor.id == user.id
        else:
            return self.is_owner(user)

    def is_owner(self, user):
        return self.owner.id == user.id

    def __str__(self):
        return "Message: '" + self.content + "' by " + self.owner.username
