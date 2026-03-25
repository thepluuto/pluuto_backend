from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Runs all seed commands to populate the database with sample data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting full database seeding...'))

        try:
            # 1. Seed Users
            self.stdout.write(self.style.SUCCESS('\n--- Seeding Users ---'))
            call_command('seed_users')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding users: {e}'))

        try:
            # 2. Seed Events (which also handles Categories)
            self.stdout.write(self.style.SUCCESS('\n--- Seeding Events and Categories ---'))
            call_command('populate_sample_events')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding events: {e}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Full seeding process completed successfully!'))
