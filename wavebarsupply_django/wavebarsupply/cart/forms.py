from django import forms


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)


class UpdateCartForm(forms.Form):
    item_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)


class RemoveCartForm(forms.Form):
    item_id = forms.IntegerField(min_value=1)


import re


class CheckoutForm(forms.Form):
    """Delivery + (simulated) card details collected in the checkout overlay.

    Card details are validated but never stored — this only simulates a payment.
    """

    # --- Delivery (prefilled from the customer, editable) ---
    name = forms.CharField(
        max_length=100, label='Full Name',
        widget=forms.TextInput(attrs={'maxlength': 100}))
    address = forms.CharField(
        max_length=200, label='Delivery Address',
        widget=forms.TextInput(attrs={'maxlength': 200}))
    phone = forms.CharField(
        max_length=20, label='Phone',
        widget=forms.TextInput(attrs={'maxlength': 20, 'inputmode': 'tel'}))
    email = forms.EmailField(
        max_length=100, label='Email',
        widget=forms.EmailInput(attrs={'maxlength': 100}))

    # --- Card (simulated) ---
    card_number = forms.CharField(
        label='Card Number',
        widget=forms.TextInput(attrs={'maxlength': 16, 'inputmode': 'numeric',
                                      'autocomplete': 'off',
                                      'placeholder': '16-digit card number'}))
    card_holder = forms.CharField(
        max_length=100, label='Card Holder Name',
        widget=forms.TextInput(attrs={'maxlength': 100}))
    expiration = forms.CharField(
        label='Expiration (MM/YY)',
        widget=forms.TextInput(attrs={'maxlength': 5, 'placeholder': 'MM/YY'}))
    cvv = forms.CharField(
        label='CVV',
        widget=forms.TextInput(attrs={'maxlength': 4, 'inputmode': 'numeric',
                                      'autocomplete': 'off', 'placeholder': 'CVV'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form_input').strip()

    def clean_card_number(self):
        value = self.cleaned_data['card_number'].replace(' ', '')
        if not value.isdigit():
            raise forms.ValidationError('Card number must contain digits only.')
        if not (13 <= len(value) <= 16):
            raise forms.ValidationError('Card number must be 13 to 16 digits.')
        return value

    def clean_cvv(self):
        value = self.cleaned_data['cvv']
        if not value.isdigit() or not (3 <= len(value) <= 4):
            raise forms.ValidationError('CVV must be 3 or 4 digits.')
        return value

    def clean_expiration(self):
        value = self.cleaned_data['expiration'].strip()
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', value):
            raise forms.ValidationError('Expiration must be in MM/YY format.')
        return value
