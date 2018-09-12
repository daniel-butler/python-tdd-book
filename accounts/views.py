from django.shortcuts import redirect
from django.core.mail import send_mail


def send_login_email(request):
    email = request.POST['email']
    print(type(send_mail))
    send_mail(
        'Your login link for Superlists',
        'body text bc',
        'noreply@lists.accounting.equipment',
        [email]
    )
    return redirect('/')
