from atexit import register
from django import template
from cryptography.fernet import Fernet
from django.conf import settings

register = template.Library()

@register.filter
def replaceBlank(value,stringVal=""):
    value = str(value).replace(stringVal,'')
    return value

@register.filter
def encryptdata(value):
    fernet = Fernet(settings.ID_ENCRYPTION_KEY)
    value  = fernet.encrypt(str(value).encode())
    return value


@register.filter(name='abs')
def absolute_value(value):
    return abs(value)

@register.filter(name='credit_or_debit')
def credit_or_debit(value):
    if value < 0:
        return  str(abs(value)) + ' بنام '
    elif value > 0:
        return str(abs(value)) + ' جمع '
    else:
        return abs(value)
    
@register.filter(name='check_value')
def check_value(value):
    """
    Custom filter to check if a value is a string or zero.
    If it's a string or zero, return the value itself, otherwise return '-'.
    """
    if value == "" or value == 0 or value == None:
        return "-"
    else:
        return value

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def invoice_type(value):
    if value == 0:
        return "Purchase"
    else:
        return "Sale"


@register.filter(name = "not_available")
def notAvailable(value):
    if value == 0:
        return "N/A"
    else:
        return value
    
@register.simple_tag
def total_without_changes(value,arg1,arg2):
    return value + arg1 - arg2