from django.core.management.base import BaseCommand
from events.models import User
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Seeds the database with example users'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to seed users...'))

        # Sample data
        users_data = [
            {
                'full_name': 'John Doe',
                'phone_number': '919876543210',
                'email': 'john.doe@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Jane Smith',
                'phone_number': '919876543211',
                'email': 'jane.smith@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Michael Johnson',
                'phone_number': '919876543212',
                'email': 'michael.j@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Emily Davis',
                'phone_number': '919876543213',
                'email': 'emily.davis@example.com',
                'auth_provider': 'google'
            },
            {
                'full_name': 'Robert Brown',
                'phone_number': '919876543214',
                'email': 'robert.brown@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Sarah Wilson',
                'phone_number': '919876543215',
                'email': 'sarah.wilson@example.com',
                'auth_provider': 'google'
            },
            {
                'full_name': 'David Martinez',
                'phone_number': '919876543216',
                'email': 'david.m@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Lisa Anderson',
                'phone_number': '919876543217',
                'email': 'lisa.anderson@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'James Taylor',
                'phone_number': '919876543218',
                'email': 'james.taylor@example.com',
                'auth_provider': 'google'
            },
            {
                'full_name': 'Maria Garcia',
                'phone_number': '919876543219',
                'email': 'maria.garcia@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Christopher Lee',
                'phone_number': '919876543220',
                'email': 'chris.lee@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Jennifer White',
                'phone_number': '919876543221',
                'email': 'jennifer.w@example.com',
                'auth_provider': 'google'
            },
            {
                'full_name': 'Daniel Harris',
                'phone_number': '919876543222',
                'email': 'daniel.harris@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Amanda Clark',
                'phone_number': '919876543223',
                'email': 'amanda.clark@example.com',
                'auth_provider': 'phone'
            },
            {
                'full_name': 'Matthew Lewis',
                'phone_number': '919876543224',
                'email': 'matthew.lewis@example.com',
                'auth_provider': 'google'
            },
        ]

        created_count = 0
        skipped_count = 0

        for user_data in users_data:
            # Check if user already exists
            if User.objects.filter(phone_number=user_data['phone_number']).exists():
                self.stdout.write(self.style.WARNING(f"User {user_data['full_name']} already exists. Skipping..."))
                skipped_count += 1
                continue

            # Create user
            user = User.objects.create_user(
                phone_number=user_data['phone_number'],
                full_name=user_data['full_name'],
                email=user_data['email'],
                auth_provider=user_data['auth_provider']
            )
            
            # Set random last login (within last 30 days)
            days_ago = random.randint(0, 30)
            user.last_login = timezone.now() - timezone.timedelta(days=days_ago)
            user.save()

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Created user: {user_data['full_name']}"))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Seeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count} users'))
        self.stdout.write(self.style.SUCCESS(f'  Skipped: {skipped_count} users (already exist)'))
