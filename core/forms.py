from django import forms
from core.models import StaffUser
from django.core.validators import RegexValidator
from django.contrib.auth.forms import *
from django.contrib.auth import get_user_model
User = get_user_model()
class SaveUser(UserCreationForm):
    pakistan_phone_validator = RegexValidator(
        regex=r'^(?:(?:\+92)|(?:0))(?:(?:3[0-9]{9})|(?:[1-9][0-9]{9}))$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=True
    )
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,required=False)
    first_name = forms.CharField(max_length=250,required=False)
    last_name = forms.CharField(max_length=250,required=False)
    question = forms.CharField(max_length=255,required=False)
    answer = forms.CharField(max_length=255,required=False)
    assigned_staff = forms.CharField(max_length=255,required=False,empty_value=None)
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ( 'username','phone_number','password1', 'password2','email','assigned_staff','first_name', 'last_name','question','answer')

class UpdateUser(UserChangeForm):
    pakistan_phone_validator = RegexValidator(
        regex=r'^(?:(?:\+92)|(?:0))(?:(?:3[0-9]{9})|(?:[1-9][0-9]{9}))$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=True
    )
    username = forms.CharField(max_length=250)
    email = forms.EmailField(max_length=250,required=False)
    first_name = forms.CharField(max_length=250,required=False)
    last_name = forms.CharField(max_length=250,required=False)
    question = forms.CharField(max_length=255,required=False)
    assigned_staff = forms.CharField(max_length=255,required=False,empty_value=None)
    answer = forms.CharField(max_length=255,required=False)
    
    class Meta:
        model = User
        fields = ('username','assigned_staff','email','phone_number','first_name', 'last_name','question','answer')

class SaveStaffUser(forms.ModelForm):
    class Meta:
        model = StaffUser
        fields = ('user',)