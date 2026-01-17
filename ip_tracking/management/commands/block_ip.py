from django.core.management.base import BaseCommand, CommandError
from .models import BlockedIP


class Command(BaseCommand):
    help = "Add an IP address to the BlockedIP blacklist."

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="IP address to block")

    def handle(self, *args, **options):
        ip_address = options["ip_address"].strip()

        obj, created = BlockedIP.objects.get_or_create(ip_address=ip_address)

        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked IP added: {ip_address}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP already blocked: {ip_address}"))
