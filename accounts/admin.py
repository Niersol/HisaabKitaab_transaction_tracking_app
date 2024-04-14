from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin
@admin.register(Party)
class PartyAdmin(ModelAdmin):
    pass