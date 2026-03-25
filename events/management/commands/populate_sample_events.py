from django.core.management.base import BaseCommand
from events.models import User, Event, EventCategory, EventGalleryImage
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the database with sample events'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # 1. Ensure Categories
        categories_data = [
            ('Music', 'Music concerts and festivals', 'active', 'artist'),
            ('Comedy', 'Stand-up comedy and shows', 'active', None),
            ('Technology', 'Tech conferences and meetups', 'active', 'event_organizer'),
            ('Art', 'Art exhibitions and galleries', 'active', 'venue_owner'),
        ]
        
        categories = {}
        for name, details, status, allowed in categories_data:
            cat, created = EventCategory.objects.get_or_create(
                name=name,
                defaults={
                    'details': details,
                    'status': status,
                    'allowed_user_type': allowed
                }
            )
            categories[name] = cat
            if created:
                self.stdout.write(f'Created category: {name}')

        # 2. Ensure Users
        users_data = [
            ('9999900001', 'John Artist', 'john@example.com', 'artist'),
            ('9999900002', 'Jane Organizer', 'jane@example.com', 'event_organizer'),
            ('9999900003', 'Bob Venue', 'bob@example.com', 'venue_owner'),
        ]

        users = []
        for phone, name, email, u_type in users_data:
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'full_name': name,
                    'email': email,
                    'user_type': u_type,
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {name}')
            users.append(user)

        # 3. Create Dummy Image
        def get_dummy_image(color='blue'):
            file = BytesIO()
            image = Image.new('RGB', (600, 400), color=color)
            image.save(file, 'JPEG')
            file.seek(0)
            return ContentFile(file.read(), 'sample.jpg')

        # 4. Create Events
        events_data = [
            {
                'title': 'Summer Music Festival',
                'category': 'Music',
                'user_idx': 0, # John Artist
                'location': 'Central Park, NY',
                'start_time': '18:00 - 23:00',
                'description': 'A massive summer music festival featuring top artists.',
                'regular_price': 50.00,
                'status': 'approved',
                'color': 'purple'
            },
            {
                'title': 'Tech Innovators Summit',
                'category': 'Technology',
                'user_idx': 1, # Jane Organizer
                'location': 'Silicon Valley Convention Center',
                'start_time': '09:00 - 17:00',
                'description': 'Join the leading minds in tech for a day of innovation.',
                'regular_price': 200.00,
                'offer_price': 150.00,
                'status': 'pending',
                'color': 'blue'
            },
            {
                'title': 'Modern Art Gallery Opening',
                'category': 'Art',
                'user_idx': 2, # Bob Venue
                'location': 'SoHo Art Space',
                'start_time': '19:00 - 22:00',
                'description': 'Exclusive opening of the new modern art collection.',
                'regular_price': 0.00,
                'status': 'approved',
                'color': 'red'
            },
            {
                'title': 'Stand-up Comedy Night',
                'category': 'Comedy',
                'user_idx': 0, # John Artist
                'location': 'The Giggle Factory',
                'start_time': '20:00 - 22:00',
                'description': 'A night of laughter with local comedians.',
                'regular_price': 20.00,
                'status': 'rejected',
                'rejection_reason': 'Incomplete description provided.',
                'color': 'green'
            },
             {
                'title': 'Indie Rock Concert',
                'category': 'Music',
                'user_idx': 0,
                'location': 'The Basement',
                'start_time': '21:00 - 02:00',
                'description': 'Local indie bands rocking the night away.',
                'regular_price': 15.00,
                'status': 'pending',
                'color': 'orange'
            }
        ]

        for data in events_data:
            # Check if event exists to avoid duplicates on re-run
            if Event.objects.filter(title=data['title']).exists():
                continue

            event = Event(
                owner=users[data['user_idx']],
                category=categories[data['category']],
                title=data['title'],
                location=data['location'],
                start_time=data['start_time'],
                description=data['description'],
                regular_price=data['regular_price'],
                offer_price=data.get('offer_price'),
                status=data['status'],
                rejection_reason=data.get('rejection_reason'),
            )
            
            # Save image
            img_content = get_dummy_image(data['color'])
            event.banner_image.save(f"banner_{data['title'].replace(' ', '_')}.jpg", img_content, save=False)
            
            event.save()
            self.stdout.write(f'Created event: {data["title"]}')

            # Add a gallery image
            gallery_img = get_dummy_image(data['color'])
            EventGalleryImage.objects.create(
                event=event, 
                image=ContentFile(gallery_img.read(), f"gallery_{data['title']}.jpg")
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated sample events'))
