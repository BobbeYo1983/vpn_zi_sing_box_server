from django.core.management.base import BaseCommand
from django.db import connection
from vpn.singbox import write_config

class Command(BaseCommand):
    help = "Generate sing-box config"

    def handle(self, *args, **options):
        # Ждём, пока таблица VpnUser готова
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vpn_vpnuser';")
            if cursor.fetchone() is None:
                self.stdout.write(self.style.WARNING("VpnUser table not found, skipping config generation"))
                return

        write_config()
        self.stdout.write(self.style.SUCCESS("Sing-box config generated"))