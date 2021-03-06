import json
from functools import reduce
from random import randint, randrange

from django.db.models import Q
from django.http import HttpResponse, HttpResponseServerError
from django.template.context_processors import csrf
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

# Create your views here.
from django.template.response import TemplateResponse

from baips2 import settings
from ps2 import models
from ps2.forms import RegistrationForm, ChangePasswordForm
from ps2.models import UserPasswords, LastUserMask


def index(request):
    return redirect('/messages/')


def messages(request):
    messages_all = models.Message.objects.all()
    action_type = request.GET.get('action')
    action_param = request.GET.get('par')
    if action_type == 'Dodaj' and request.user.is_authenticated():
        new_message = models.Message()
        if action_param:
            new_message.content = action_param
            new_message.owner = request.user
            new_message.save()
    if action_type == "Usuń":
        message_to_delete = models.Message.objects.get(id=action_param)
        if message_to_delete and message_to_delete.owner == request.user:
            message_to_delete.delete()
    if action_type == "Wyloguj":
        return redirect('/logout/')
    if action_type == "Edytuj":
        return edit_message(request)

    context = {'show_login_button': True, 'messages': messages_all}
    if request.user.is_authenticated():
        context['login_info'] = {}
        secondLastSuccesfulLogin = models.UserLoginInfo.getSecondLastSuccessfulLogin(request.user.username)
        context['login_info'][
            'last_successful_login'] = secondLastSuccesfulLogin.login_attempt_date if secondLastSuccesfulLogin is not None else ''
        lastUnsuccessfulLogin = models.UserLoginInfo.getLastUnsuccessfulLogin(request.user.username)
        context['login_info'][
            'last_unsuccessful_login'] = lastUnsuccessfulLogin.login_attempt_date if lastUnsuccessfulLogin is not None else ''
        lastUnsuccessfulLoginCount = models.UserLoginInfo.getUnsuccesfulLoginTriesAfterSecondLastSuccessful(
            request.user.username)
        context['login_info'][
            'last_unsuccessful_login_count'] = lastUnsuccessfulLoginCount if lastUnsuccessfulLoginCount is not None else ''

    return TemplateResponse(request, 'messages.html', context)

@login_required
def edit_message(request):
    if request.GET.get('confirm') and request.GET.get('message_id') and request.GET.get('message_content'):
        message_to_edit = models.Message.objects.get(id=request.GET.get('message_id'))
        if message_to_edit.can_content_be_edited_by(request.user):
            message_to_edit.content = request.GET.get('message_content')
            if message_to_edit.is_owner(request.user):
                if request.GET.getlist('editor_id'):
                    editors_queries = [Q(id=editor_id) for editor_id in request.GET.getlist('editor_id')] # tutaj dzieje sie wtf
                    query = editors_queries.pop()
                    for other_query in editors_queries:
                        query |= other_query
                    editors = User.objects.filter(query)
                    message_to_edit.editors = editors
                else:
                    message_to_edit.editors = User.objects.none()
            message_to_edit.save()
        return redirect('/messages/')
    else:
        action_param = request.GET.get('par')
        message_to_edit = models.Message.objects.get(id=action_param)
        if message_to_edit:
            if message_to_edit.can_content_be_edited_by(request.user):
                all_users = models.User.objects.all()
                editors_ids = [editor.id for editor in message_to_edit.editors.all()]
                return TemplateResponse(request, 'edit_message.html',
                                        {'all_users': all_users, 'editor_ids': editors_ids, 'message': message_to_edit})
            else:
                return redirect('/messages/')
        else:
            return redirect('/messages/')


def prelogin(request):
    return TemplateResponse(request, 'prelogin.html')


def register(request):
    # if request.method == 'POST':
    if 'username' in request.GET and 'password1' in request.GET and 'password2' in request.GET:
        form = RegistrationForm(request.GET)
        if form.is_valid():
            user = form.save()
            return TemplateResponse(request, 'prelogin.html')
        else:
            token = {'form': RegistrationForm()}
            token.update(csrf(request))
            token['error'] = json.dumps(form.errors)
            return TemplateResponse(request, "register.html", token)
    else:
        token = {'form': RegistrationForm()}
        token.update(csrf(request))
        return TemplateResponse(request, "register.html", token)


def log_in(request):
    pre_username = request.GET.get('pre_username')
    if pre_username is not None:
        try:
            user = User.objects.get(username=pre_username)
            previous_mask = None
            try:
                previous_mask = LastUserMask.objects.get(username=pre_username, passed=False)
            except:
                pass
            if previous_mask is not None:
                user_mask = previous_mask.mask
            else:
                user_p = UserPasswords.objects.filter(user=user)
                count = len(user_p)
                random_user_p = randint(0, count - 1)
                user_mask = user_p[random_user_p].mask
                next_mask = LastUserMask()
                next_mask.username = pre_username
                next_mask.mask = user_mask
                next_mask.save()
        except User.DoesNotExist or UserPasswords.DoesNotExist:
            # Run the default password hasher twice to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password('randomtest')
            User().set_password('randomtest')
            previous_mask = None
            try:
                previous_mask = LastUserMask.objects.get(username=pre_username, passed=False)
            except:
                pass
            if previous_mask is not None:
                user_mask = previous_mask.mask
            else:
                fake_pass_len = randrange(8, 15)
                p_size = randint(5, fake_pass_len)
                tmp_psw = set()
                while len(tmp_psw) != p_size:
                    tmp_psw.add(randint(0, fake_pass_len))
                user_mask = reduce(lambda x, y: x + y, map(lambda x: (2 ** x), tmp_psw))
                next_mask = LastUserMask()
                next_mask.username = pre_username
                next_mask.mask = user_mask
                next_mask.save()

        return TemplateResponse(request, 'login.html', {'p_username': pre_username, 'mask': user_mask})
    else:
        bad_cred = 'Zły login lub hasło!'
        if request.user.is_authenticated():
            return redirect('/messages/')
        username = request.GET.get('username')
        mask = 0
        password = ""

        for x in range(16):
            part = request.GET.get(str(x))
            if part is not None:
                mask += 2 ** x
                password += str(part)

        lastMask = LastUserMask.objects.get(username=username, passed=False)

        if username and password and mask:
            user_login_attempt = models.UserLoginInfo()
            user_login_attempt.user = username
            now = timezone.now()
            user_login_attempt.login_attempt_date = now

            previous_unsuccesful_login = models.UserLoginInfo.getLastUnsuccessfulLogin(username)
            login_count = models.UserLoginInfo.getUnsuccesfulLoginTriesAfterLastSuccessful(username)

            if previous_unsuccesful_login is not None:
                next_login_time = previous_unsuccesful_login.login_attempt_date + timezone.timedelta(
                    seconds=(5 * login_count))
                if next_login_time > now:
                    # next_login_time = now + timezone.timedelta(minutes=(1 * (login_count + 1)))
                    return TemplateResponse(request, 'prelogin.html', {
                        'error': "Z powodu zbyt wielu błędów użytkownik został zablokowany do " + str(next_login_time)})

            try:
                if mask != lastMask.mask:
                    raise Exception('Invalid credentials')
                if login_count is not None:
                    if login_count > settings.LOGIN_ATTEMPTS_MAX_ERRORS:
                        user = User.objects.get(username=username)
                        user.is_active = False
                        user.save()
                        raise Exception("Uzytkownik jest zablokowany, skontaktuj się z administratorem")
                try:
                    user = User.objects.get(username=username)
                    user_p = UserPasswords.objects.get(user=user, mask=mask)
                except:
                    raise Exception("Invalid credentials")
                if user_p.check_password(password) and user is not None:
                    try:
                        previous_mask = LastUserMask.objects.get(username=username, passed=False)
                        previous_mask.passed = True
                        previous_mask.save()
                    except:
                        pass
                    login(request, user)
                    user_login_attempt.is_login_successful = True
                    return redirect('/messages/', request=request)
                else:
                    raise Exception(bad_cred)

            except Exception as e:
                user_login_attempt.is_login_successful = False
                return TemplateResponse(request, 'prelogin.html', {'error': e})
            finally:
                if user_login_attempt.is_login_successful is None:
                    user_login_attempt.is_login_successful = False
                user_login_attempt.save()
        else:
            return TemplateResponse(request, 'prelogin.html', {'error': "Invalid credentials"})


@login_required
def change_password(request):
    request_params = (
    request.GET.get('old_password'), request.GET.get('new_password1'), request.GET.get('new_password2'))
    print(request.GET)
    if not any(param is None for param in request_params):
        form = ChangePasswordForm(user=request.user, data=request.GET)
        if form.is_valid():
            form.save()
            return redirect('/messages/')
        else:
            token = {'form': ChangePasswordForm(user=request.user)}
            token.update(csrf(request))
            token['error'] = json.dumps(form.errors)
            return TemplateResponse(request, "change_password.html", token)
    else:
        token = {'form': ChangePasswordForm(user=request.user)}
        token.update(csrf(request))
        return TemplateResponse(request, 'change_password.html', token)


@login_required
def log_out(request):
    logout(request)
    return redirect('/messages/')
