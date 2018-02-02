from django import forms


class ClaimForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form__input form__input_name',
        'placeholder': 'First Name',
    }))

    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form__input form__input_name',
        'placeholder': 'Last Name',
    }))

    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Email',
    }))

    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Phone',
    }))

    business_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Name of Business',
    }))

    business_address = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form__input',
        'placeholder': 'Business Address',
    }))
