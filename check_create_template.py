import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_project.settings')
django.setup()

from django.template.loader import get_template

try:
    template = get_template('events/admin/event_create.html')
    print('Template loaded successfully!')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
