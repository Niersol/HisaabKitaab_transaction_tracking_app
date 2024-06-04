from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count,Q
from django.core.exceptions import ValidationError

class Party(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255,blank=True,null=True)
    address = models.CharField(max_length=255,blank=True,null=True)
    delete_flag = models.IntegerField(default=0)
    
    def __str__(self):
        return f'{self.name}'

    class Meta:
        unique_together = ['user','name']

    def clean(self):
        if (self.user.staffuser if hasattr(self.user, 'staffuser') else False) or self.user.is_superuser:
            raise ValidationError("A staff user cannot be associated with a party.")
        super().clean()
        
    def get_total_debit(self):
        transactions = self.transaction_set.filter(delete_flag=0)
        total_debit = sum(transaction.debit for transaction in transactions)
        return total_debit

    def get_total_credit(self):
        transactions = self.transaction_set.filter(delete_flag=0)
        total_credit = sum(transaction.credit for transaction in transactions)
        return total_credit
    def get_balance(self):
        total_debit = self.get_total_debit()
        total_credit = self.get_total_credit()
        balance = total_debit - total_credit
        return balance

class Form(models.Model):
    created_at = models.DateField(unique=True)
    
class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    delete_flag = models.IntegerField(default=0)
    def __str__(self) -> str:
        return self.name
    
class Transaction(models.Model):
    party = models.ForeignKey(Party,on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)
    debit = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    time = models.TimeField(auto_now_add=True)
    form = models.ForeignKey(Form,on_delete = models.CASCADE)
    delete_flag = models.IntegerField(default=0)
    def __str__(self):
        return self.party.name  
    
    class Meta:
        permissions = (
            ("can_manage_transactions","Can Manage Transactions"),
        )

    def get_running_balance(self):
        prior_transactions = Transaction.objects.filter(
            Q(form__created_at__lt=self.form.created_at) | (Q(form__created_at=self.form.created_at, time__lt=self.time)),
            delete_flag=0,
            party=self.party,
        )
        prior_debit = sum(transaction.debit for transaction in prior_transactions)
        prior_credit = sum(transaction.credit for transaction in prior_transactions)

        running_balance = prior_debit - prior_credit
        return running_balance + self.debit - self.credit
    
class Trade(models.Model):
    transaction = models.OneToOneField(Transaction,on_delete=models.CASCADE,blank=True,null=True)
    bill_number = models.PositiveIntegerField(default=0)
    party = models.ForeignKey(Party,on_delete=models.CASCADE)
    description = models.TextField(blank=True,null=True)
    debit = models.PositiveIntegerField(default=0)
    credit = models.PositiveIntegerField(default=0)
    time = models.TimeField(auto_now_add=True)
    form = models.ForeignKey(Form,on_delete = models.CASCADE)
    delete_flag = models.IntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    is_sales = models.BooleanField()
    def __str__(self):
            return self.party.name  
    class Meta:
        permissions = (
            ("can_manage_sales","Can Manage Sales"),
            ("can_manage_purchase","Can Manage Purchase"),
            
        )

class TradeItem(models.Model):

    trade = models.ForeignKey(Trade,on_delete=models.CASCADE,related_name='trade_items') 
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"{self.trade} - {self.product}"

