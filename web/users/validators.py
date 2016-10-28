from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


def validate_pwd(pwd, pwd2):
    if not pwd or not pwd2:
        raise ValidationError('Password is required')

    if len(pwd) < 6:
        raise ValidationError('Password should be at least 6 characters')

    if not set('[~!@#$%^&*()_-+={}":;\',.<>\|/?]+$').intersection(pwd):
        raise ValidationError('Password should contain at least 1 special character')

    if pwd != pwd2:
        raise ValidationError('Passwords don\'t match')


def validate_email(email):
    if not email:
        raise ValidationError('Email is required')

    try:
        validator = EmailValidator()
        validator.__call__(email)
    except ValidationError:
        raise ValidationError('Invalid email format')
