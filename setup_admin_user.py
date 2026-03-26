import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_project.settings')
django.setup()

from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    phone = '8129800342'
    email = 'admin@example.com'
    password = 'admin@123'
    
    user, created = User.objects.get_or_create(phone_number=phone)
    user.email = email
    user.full_name = 'Administrator'
    user.set_password(password)
    user.user_type = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    print(f"Successfully configured superuser.")
    print(f"Phone: {phone}")
    print(f"Password: {password}")
    print(f"Email: {email}")

except Exception as e:
    print(f"Error: {e}")
