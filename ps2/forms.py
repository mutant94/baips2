from functools import reduce
from random import randint

from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from django.contrib.auth.models import User
from ps2.models import UserPasswords
from ps2.passwords import baips_passwords


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Ninja007'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = '********'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = '********'

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        passw = self.cleaned_data["password1"]

        user_passwords = baips_passwords.generate_user_passwords_entities(passw)
        user.set_password(passw)
        if commit:
            user.save()
            for up in user_passwords:
                up.user = user
                up.save()

        return user


class ChangePasswordForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = "Old password"
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = '********'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = '********'

    def save(self, commit=True):
        user_with_changed_password = super(PasswordChangeForm, self).save(commit=False)
        new_password = self.cleaned_data['new_password1']
        user_with_changed_password.set_password(new_password)
        new_user_passwords = baips_passwords.generate_user_passwords_entities(new_password)
        UserPasswords.objects.filter(user=user_with_changed_password).delete()
        if commit:
            user_with_changed_password.save()
            for user_password in new_user_passwords:
                user_password.user = user_with_changed_password
                user_password.save()

        return user_with_changed_password

    # def clean_old_password(self):
    #     old_password = self.cleaned_data["old_password"]
    #     random_user_passwords = UserPasswords.objects.filter(user=self.user)
    #     random_password_index = randint(0, len(random_user_passwords))
    #     user_password_to_validate = random_user_passwords[random_password_index]
    #     password_mask = user_password_to_validate.mask
    #     # if not self.user.check_password(old_password):
    #     raise forms.ValidationError(
    #         self.error_messages['password_incorrect'],
    #         code='password_incorrect',
    #     )
    #     return old_password
