from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


User = get_user_model()

DUPLICATE_EMAIL = _(u"This email address is already in use. "
                    u"Please supply a different email address.")

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        help_text=_(u'email address'),
        required=True,
    )

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(DUPLICATE_EMAIL)
        return self.cleaned_data['email']

    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'password1',
            'password2',
            'email',
        ]




