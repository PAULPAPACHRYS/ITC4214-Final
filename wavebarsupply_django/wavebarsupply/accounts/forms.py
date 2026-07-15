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
    """The tidying and checking shared by the sign-up and account-edit forms.

    Both forms edit the same user details, so the rules live in one place: if
    they were written twice they could drift apart.
    """

    def apply_field_hints(self):
        """Add the browser-side hints to whichever of these fields the form has.

        The server still checks everything; these only make the browser catch a
        mistake sooner. Keeping them in one method means the phone pattern is
        written once instead of in every form.
        """
        for field in ('first_name', 'last_name'):
            if field in self.fields:
                self.fields[field].widget.attrs['data-name-check'] = 'true'
        if 'phone' in self.fields:
            # input_type, not attrs['type']: Django renders the type from the
            # widget itself, so an attrs['type'] would simply be ignored.
            # type="tel" makes phones show a number keypad.
            self.fields['phone'].widget.input_type = 'tel'
            self.fields['phone'].widget.attrs['pattern'] = PHONE_PATTERN

    def clean_first_name(self):
        return clean_text(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return clean_text(self.cleaned_data['last_name'])

    def clean_bar_name(self):
        return clean_text(self.cleaned_data.get('bar_name', ''))

    def clean_email(self):
        # Lowercased, so 'Test@Bar.com' and 'test@bar.com' cannot become two
        # separate accounts. Because the value is lowercased BEFORE the
        # uniqueness check runs, the check now catches that case too.
        email = clean_email(self.cleaned_data['email'])
        clash = Users.objects.filter(email=email)
        if self.instance and self.instance.pk:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class RegisterForm(UserFieldsMixin, UserCreationForm):
    """Django's built-in UserCreationForm, extended with the trade-account
    fields. It provides password1/password2 and hashes the password on save().
    """

    # The validators are the guarantee (they run on the server). The widget
    # attributes are the convenience: the browser refuses the value before the
    # form is even sent. data-name-check is picked up by static/js/name_check.js,
    # which does the letters-any-alphabet test that an HTML pattern cannot do
    # reliably across browsers.
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
    """Django's built-in AuthenticationForm, relabelled to log in by email."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email Address'
        self.fields['username'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': 'you@yourbar.com'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form_input', 'placeholder': '******'})

    def clean_username(self):
        # Addresses are stored lowercase, and the lookup that logs a person in
        # is case-sensitive. Without this, someone who types 'Nikos@Bar.com'
        # instead of 'nikos@bar.com' would be told their details are wrong.
        return clean_email(self.cleaned_data['username'])


class AccountEditForm(UserFieldsMixin, forms.ModelForm):
    """Lets a logged-in user edit their own details. Role is NOT included here,
    so users cannot change their own role.

    It reuses UserFieldsMixin, so editing a name or email here is held to exactly
    the same rules as signing up with one.
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
        help_texts = {'phone': 'e.g. +30 6900 111111'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form_input')
        self.apply_field_hints()
