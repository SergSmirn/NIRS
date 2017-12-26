from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User


def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            domain = get_current_site(request).domain
            protocol = 'https' if request.is_secure() else 'http'
            message = render_to_string('email_confirm_message.html', {
                'domain': domain,
                'protocol': protocol,
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            subject = 'Активация аккаунта'
            to_email = form.cleaned_data.get('email')
            send_mail(subject, message, 'spelsapp@gmail.com', [to_email], fail_silently=False)
            return redirect('email_confirm')
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'email_confirm_done.html')
    else:
        return render(request, 'email_confirm_fall.html')