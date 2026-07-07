from django import forms


class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)


class UpdateCartForm(forms.Form):
    item_id = forms.IntegerField(min_value=1)
    quantity = forms.IntegerField(min_value=1)


class RemoveCartForm(forms.Form):
    item_id = forms.IntegerField(min_value=1)
