from django.contrib import admin
from .models import *
from unfold.admin import ModelAdmin
@admin.register(Party)
class PartyAdmin(ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    pass

@admin.register(Trade)
class TradeAdmin(ModelAdmin):
    pass

@admin.register(TradeItem)
class TradeItemAdmin(ModelAdmin):
    pass