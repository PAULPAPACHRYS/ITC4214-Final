from django import forms


class ContactForm(forms.Form):
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
