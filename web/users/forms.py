from django import forms
from django.contrib.auth.forms import UserCreationForm as OriginalUserCreationForm


from .models import User


class UserCreationForm(OriginalUserCreationForm):
    agree_terms = forms.BooleanField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'is_age_verified')
