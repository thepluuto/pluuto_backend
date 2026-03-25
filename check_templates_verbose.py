import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_project.settings')
django.setup()

from django.template.loader import get_template

try:
    print("Loading event_create.html...")
    template = get_template('events/admin/event_create.html')
    print('event_create.html loaded successfully!')
except Exception as e:
    print(f'Error in event_create.html: {str(e)}')
    sys.exit(1)

try:
    print("Loading event_detail_v2.html...")
    template = get_template('events/admin/event_detail_v2.html')
    print('event_detail_v2.html loaded successfully!')
except Exception as e:
    print(f'Error in event_detail_v2.html: {str(e)}')
    sys.exit(1)

print("\nBoth templates loaded successfully!")
