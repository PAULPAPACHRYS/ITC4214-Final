from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile

LOCATION_CHOICES = [
    ('', 'Select your region…'),
    ('Attica', 'Attica'), ('Mykonos', 'Mykonos'), ('Santorini', 'Santorini'),
    ('Rhodes', 'Rhodes'), ('Corfu', 'Corfu'), ('Crete', 'Crete'),
    ('Paros', 'Paros'), ('Ios', 'Ios'), ('Zakynthos', 'Zakynthos'),
    ('Halkidiki', 'Halkidiki'), ('Other', 'Other'),
]


class LoginForm(AuthenticationForm):
    """Django's built-in auth form, restyled and relabelled to use email."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['username'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': 'you@yourbar.com'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': '******'})


class RegisterForm(UserCreationForm):
    """Built-in UserCreationForm extended with the trade-account fields.

    The account's email doubles as its username, so members log in with email.
    """

    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    bar_name = forms.CharField(max_length=100, label='Beach Bar / Business Name')
    email = forms.EmailField(max_length=100, label='Email Address')
    phone = forms.CharField(max_length=20, label='Phone Number')
    location = forms.ChoiceField(choices=LOCATION_CHOICES, label='Location / Region')
    terms = forms.BooleanField(
        label='I agree to the Terms & Conditions and Privacy Policy')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Give every visible field the shared input style.
        for name, field in self.fields.items():
            if name != 'terms':
                field.widget.attrs.setdefault('class', 'form_input')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                bar_name=self.cleaned_data['bar_name'],
                phone=self.cleaned_data['phone'],
                location=self.cleaned_data['location'],
            )
        return user
