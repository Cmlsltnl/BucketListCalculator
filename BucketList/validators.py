from django.core.exceptions import ValidationError

def validate_positive(value):
    if 0 > value:
        raise ValidationError('%s is not a positive number' % value)
        