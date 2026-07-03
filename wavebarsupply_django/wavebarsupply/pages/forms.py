from django import forms


class ContactForm(forms.Form):
    """Built with Django's forms framework so validation is handled server-side.

    max_length is enforced by Django on the server; the matching maxlength on the
    widgets also stops the browser accepting over-long input.
    """

    email = forms.EmailField(
        max_length=100,
        label='Email Address',
        widget=forms.EmailInput(attrs={'maxlength': 100, 'placeholder': 'you@yourbar.com'}),
    )
    bar_name = forms.CharField(
        max_length=100,
        label='Bar Name',
        widget=forms.TextInput(attrs={'maxlength': 100, 'placeholder': 'Sunset Beach Bar'}),
    )
    message = forms.CharField(
        max_length=500,
        label='Message',
        widget=forms.Textarea(attrs={'maxlength': 500, 'placeholder': 'How can we help?'}),
    )
