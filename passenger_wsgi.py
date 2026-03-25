import os
import sys

# imports the project settings
# make sure to point to your project's settings.py
sys.path.append(os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'event_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
