from django.shortcuts import redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.core.urlresolvers import reverse

from accounts.models import Token


def send_login_email(request):
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to login:\n{url}'
    send_mail(
        'Your login link for Superlists',
        message_body,
        'noreply@lists.accounting.equipment',
        [email]
    )
    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in."
    )
    return redirect('/')

def login(request):
    return redirect('/')
