from django import forms

from .models import Preset


class ColorInput(forms.TextInput):
    """A normal text input rendered as the browser's native colour picker."""
    input_type = 'color'


class PresetForm(forms.ModelForm):
    class Meta:
        model = Preset
        fields = ['name', 'color', 'ingredients']
        widgets = {
            'name': forms.TextInput(attrs={
                'maxlength': 100, 'placeholder': 'e.g. Negroni', 'class': 'form_input'}),
            'color': ColorInput(attrs={'class': 'preset_color_input'}),
        }

    def clean_ingredients(self):
        ingredients = self.cleaned_data.get('ingredients')
        if not ingredients:
            raise forms.ValidationError('Add at least one ingredient.')
        return ingredients
