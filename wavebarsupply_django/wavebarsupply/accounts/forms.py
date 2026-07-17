from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Users
from .validators import (PHONE_PATTERN, clean_email, clean_text,
                         name_validator, phone_validator)

LOCATION_CHOICES = [
    ('', 'Select your region…'),
    ('Attica', 'Attica'), ('Mykonos', 'Mykonos'), ('Santorini', 'Santorini'),
    ('Rhodes', 'Rhodes'), ('Corfu', 'Corfu'), ('Crete', 'Crete'),
    ('Paros', 'Paros'), ('Ios', 'Ios'), ('Zakynthos', 'Zakynthos'),
    ('Halkidiki', 'Halkidiki'), ('Other', 'Other'),
]


class UserFieldsMixin:
    def apply_field_hints(self):
        for field in ('first_name', 'last_name'):
            if field in self.fields:
                self.fields[field].widget.attrs['data-name-check'] = 'true'
        if 'phone' in self.fields:
            self.fields['phone'].widget.input_type = 'tel'
            self.fields['phone'].widget.attrs['pattern'] = PHONE_PATTERN

    def clean_first_name(self):
        return clean_text(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return clean_text(self.cleaned_data['last_name'])

    def clean_bar_name(self):
        return clean_text(self.cleaned_data.get('bar_name', ''))

    def clean_email(self):
        email = clean_email(self.cleaned_data['email'])
        clash = Users.objects.filter(email=email)
        if self.instance and self.instance.pk:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class RegisterForm(UserFieldsMixin, UserCreationForm):
    first_name = forms.CharField(max_length=50, label='First Name',
                                 validators=[name_validator])
    last_name = forms.CharField(max_length=50, label='Last Name',
                                validators=[name_validator])
    bar_name = forms.CharField(max_length=100, label='Beach Bar / Business Name')
    email = forms.EmailField(max_length=100, label='Email Address')
    phone = forms.CharField(max_length=20, label='Phone Number',
                            validators=[phone_validator],
                            help_text='e.g. +30 6900 111111')
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
        self.apply_field_hints()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['username'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': 'you@yourbar.com'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': '******'})

    def clean_username(self):
        return clean_email(self.cleaned_data['username'])


class AccountEditForm(UserFieldsMixin, forms.ModelForm):
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
        help_texts = {'phone': 'e.g. +30 6900 111111'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form_input')
        self.apply_field_hints()
