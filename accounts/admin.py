from django.contrib import admin
from .models import *
@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(TradeItem)
class TradeItemAdmin(admin.ModelAdmin):
    pass
@admin.register(Transaction)
class TransactionItemAdmin(admin.ModelAdmin):
    pass