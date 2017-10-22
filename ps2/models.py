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


class UserLoginInfo(models.Model):
    user = models.CharField(max_length=255)
    login_attempt_date = models.DateTimeField()
    is_login_successful = models.BooleanField()

    @staticmethod
    def getLastSuccessfulLogin(user):
        res = UserLoginInfo.objects.filter(is_login_successful=True, user=user).order_by("-id")
        if res.count() > 0:
            return res[0]
        else:
            return None

    @staticmethod
    def getSecondLastSuccessfulLogin(user):
        res = UserLoginInfo.objects.filter(is_login_successful=True, user=user).order_by("-id")
        if res.count() > 1:
            return res[1]
        else:
            return None

    @staticmethod
    def getLastUnsuccessfulLogin(user):
        res = UserLoginInfo.objects.filter(is_login_successful=False, user=user).order_by("-id")
        if res.count() > 0:
            return res[0]
        else:
            return None

    @staticmethod
    def getUnsuccesfulLoginTriesAfterSecondLastSuccessful(user):
        secondLastSuccesfulLogin = UserLoginInfo.getSecondLastSuccessfulLogin(user)
        if secondLastSuccesfulLogin is not None:
            return UserLoginInfo.objects.filter(
                login_attempt_date__gt=secondLastSuccesfulLogin.login_attempt_date, is_login_successful=False).count()
        else:
            return None

    @staticmethod
    def getUnsuccesfulLoginTriesAfterLastSuccessful(user):
        lastSuccesfulLogin = UserLoginInfo.getLastSuccessfulLogin(user)
        if lastSuccesfulLogin is not None:
            return UserLoginInfo.objects.filter(login_attempt_date__gt=lastSuccesfulLogin.login_attempt_date).count()
        else:
            return None
