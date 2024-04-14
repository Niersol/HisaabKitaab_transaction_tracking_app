from django import forms
from accounts import models
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm,PasswordResetForm
from django.contrib.auth import  get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q  # Add this import
from django.db import IntegrityError

class SaveParty(forms.ModelForm):
    name = forms.CharField(max_length=255,required=True)
    address = forms.TextInput()
    pakistan_phone_validator = RegexValidator(
        regex=r'^(?:(?:\+92)|(?:0))(?:(?:3[0-9]{9})|(?:[1-9][0-9]{9}))$',
        message='Enter a valid phone number.',
    )
    phone_number = forms.CharField(
        label='Phone Number',
        validators=[pakistan_phone_validator],
        required=False
    )
    class Meta:
        model = models.Party
        fields = ['user', 'name', 'phone_number', 'address']

class SaveForm(forms.ModelForm):
    description = forms.TextInput()
    debit = forms.IntegerField(required=False)
    credit = forms.IntegerField(required=False)
    form = forms.IntegerField(required=False)
    party = forms.IntegerField(required=False)
    class Meta:
        model = models.Transaction
        fields = ['description','debit','credit','party','form']
    
