import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_project.settings')
django.setup()

from django.template.loader import get_template

error_file = open('template_error.txt', 'w', encoding='utf-8')

try:
    print("Loading event_create.html...")
    template = get_template('events/admin/event_create.html')
    print('event_create.html loaded successfully!')
except Exception as e:
    error_msg = f'Error in event_create.html:\n{str(e)}\n'
    print(error_msg)
    error_file.write(error_msg)
    error_file.close()
    sys.exit(1)

try:
    print("Loading event_detail_v2.html...")
    template = get_template('events/admin/event_detail_v2.html')
    print('event_detail_v2.html loaded successfully!')
except Exception as e:
    error_msg = f'Error in event_detail_v2.html:\n{str(e)}\n'
    print(error_msg)
    error_file.write(error_msg)
    error_file.close()
    sys.exit(1)

error_file.close()
print("\nBoth templates loaded successfully!")
