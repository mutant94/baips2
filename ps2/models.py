from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Message(models.Model):
    content = models.CharField(max_length=255)
    owner = models.ForeignKey(User)
    editors = models.ManyToManyField(User, related_name='editor_user', blank=True)

    def can_content_be_edited_by(self, user):
        return self.is_owner(user) or self.is_editor(user)

    def is_owner(self, user):
        return self.owner.id == user.id

    def is_editor(self, user):
        editors = self.editors.all()
        for editor in editors:
            if editor.id == user.id:
                return True
        return False

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
                login_attempt_date__gt=secondLastSuccesfulLogin.login_attempt_date, is_login_successful=False,
                user=user).count()
        else:
            return None

    @staticmethod
    def getUnsuccesfulLoginTriesAfterLastSuccessful(user):
        lastSuccesfulLogin = UserLoginInfo.getLastSuccessfulLogin(user)
        if lastSuccesfulLogin is not None:
            return UserLoginInfo.objects.filter(login_attempt_date__gt=lastSuccesfulLogin.login_attempt_date, user=user).count()
        else:
            return UserLoginInfo.objects.filter(user=user).count()


class UserPasswords(AbstractBaseUser):
    def get_short_name(self):
        pass

    def get_full_name(self):
        pass

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mask = models.IntegerField()


class LastUserMask(models.Model):
    username = models.CharField(max_length=255)
    mask = models.IntegerField()
    passed = models.BooleanField(default=False)


class UserLoginSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shouldBlock = models.BooleanField(default=False)
