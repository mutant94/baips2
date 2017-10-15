from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect

# Create your views here.
from django.template.response import TemplateResponse

from ps2 import models


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

    return TemplateResponse(request, 'messages.html', {'show_login_button': True, 'messages': messages_all})


def edit_message(request):
    if request.GET.get('confirm') and request.GET.get('message_id') and request.GET.get('message_content'):
        message_to_edit = models.Message.objects.get(id=request.GET.get('message_id'))
        message_to_edit.content = request.GET.get('message_content')
        if message_to_edit.is_owner(request.user):
            if request.GET.get('editor_id'):
                editor = models.User.objects.get(id=request.GET.get('editor_id'))
                message_to_edit.editor = editor
            else:
                message_to_edit.editor = None
        message_to_edit.save()
        return redirect('/messages/')
    else:
        action_param = request.GET.get('par')
        message_to_edit = models.Message.objects.get(id=action_param)
        if message_to_edit:
            if message_to_edit.can_content_be_edited_by(request.user):
                all_users = models.User.objects.all()
                return TemplateResponse(request, 'edit_message.html', {'all_users': all_users, 'message': message_to_edit})
            else:
                return redirect('/messages/')
        else:
            return redirect('/messages/')


def log_in(request):
    if request.user.is_authenticated():
        return redirect('/messages/')
    username = request.GET.get('username')
    password = request.GET.get('password')

    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/messages/')
        else:
            return TemplateResponse(request, 'login.html', {'error': 'wrong credentials'})
    else:
        return TemplateResponse(request, 'login.html', {'show_login_button': False})


def log_out(request):
    logout(request)
    return redirect('/messages/')
