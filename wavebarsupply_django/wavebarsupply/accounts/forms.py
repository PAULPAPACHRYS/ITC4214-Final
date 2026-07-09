from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Users

LOCATION_CHOICES = [
    ('', 'Select your region…'),
    ('Attica', 'Attica'), ('Mykonos', 'Mykonos'), ('Santorini', 'Santorini'),
    ('Rhodes', 'Rhodes'), ('Corfu', 'Corfu'), ('Crete', 'Crete'),
    ('Paros', 'Paros'), ('Ios', 'Ios'), ('Zakynthos', 'Zakynthos'),
    ('Halkidiki', 'Halkidiki'), ('Other', 'Other'),
]


class RegisterForm(UserCreationForm):
    """Django's built-in UserCreationForm, extended with the trade-account
    fields. It provides password1/password2 and hashes the password on save().
    """

    first_name = forms.CharField(max_length=50, label='First Name')
    last_name = forms.CharField(max_length=50, label='Last Name')
    bar_name = forms.CharField(max_length=100, label='Beach Bar / Business Name')
    email = forms.EmailField(max_length=100, label='Email Address')
    phone = forms.CharField(max_length=20, label='Phone Number')
    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, label='Location / Region')
    terms = forms.BooleanField(
        label='I agree to the Terms & Conditions and Privacy Policy')

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'bar_name', 'email', 'phone', 'bar_location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'terms':
                field.widget.attrs.setdefault('class', 'form_input')


class LoginForm(AuthenticationForm):
    """Django's built-in AuthenticationForm, relabelled to log in by email."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['username'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': 'you@yourbar.com'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': '******'})


class AccountEditForm(forms.ModelForm):
    """Lets a logged-in user edit their own details. Role is NOT included here,
    so users cannot change their own role.
    """

    bar_location = forms.ChoiceField(choices=LOCATION_CHOICES, label='Location / Region')

    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email', 'phone', 'bar_name', 'bar_location']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'bar_name': 'Beach Bar / Business Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form_input')
