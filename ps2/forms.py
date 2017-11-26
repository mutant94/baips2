from functools import reduce
from random import randint

from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from ps2.models import UserPasswords


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
        masks = []
        ups = []
        x = 0
        while x != 10:
            p_size = randint(5, len(passw) - 1)
            up = UserPasswords()
            tmp_psw = set()
            while len(tmp_psw) != p_size:
                tmp_psw.add(randint(0, len(passw) - 1))
            tmp_mask = reduce(lambda x, y: x + y, map(lambda x: (2 ** x), tmp_psw))
            if tmp_mask not in masks:
                masks.append(tmp_mask)
                x += 1
            else:
                continue
            up.mask = tmp_mask
            up.set_password("".join(map(lambda x: passw[x], tmp_psw)))
            ups.append(up)

        if commit:
            user.save()
            for up in ups:
                up.user = user
                up.save()

        return user
