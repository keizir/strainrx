from django import forms


class KioskEmailForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Enter Email Address',
    }))
