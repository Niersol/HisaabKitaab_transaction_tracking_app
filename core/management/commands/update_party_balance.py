from django.core.management.base import BaseCommand
from accounts.models import Party

class Command(BaseCommand):
    help = 'Update the balance field for all Party instances'

    def handle(self, *args, **kwargs):
        parties = Party.objects.all()
        for party in parties:
            balance = party.get_balance()
            party.balance = balance
            party.save()
            self.stdout.write(self.style.SUCCESS(f'Updated balance for Party {party.name}: {balance}'))
