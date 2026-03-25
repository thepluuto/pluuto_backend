from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import random
import random
import string
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, email=None, **extra_fields):
        # Allow phone_number to be None if auth_provider is google or if explicitly handled
        if not phone_number and extra_fields.get('auth_provider') != 'google':
             raise ValueError('The Phone Number field must be set')
        extra_fields.setdefault('is_active', True)
        
        user = self.model(phone_number=phone_number, **extra_fields)
        if email:
            user.email = self.normalize_email(email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    username = None
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True, null=True, blank=True)
    country_code = models.CharField(max_length=5, blank=True, null=True)
    full_name = models.CharField(_('full name'), max_length=255, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    
    AUTH_PROVIDERS = (
        ('email', 'Email'),
        ('google', 'Google'),
        ('phone', 'Phone'),
    )
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDERS, default='phone')
    
    USER_TYPES = (
        ('regular', 'Regular User'),
        ('artist', 'Artist'),
        ('event_organizer', 'Event Organizer'),
        ('experience_provider', 'Experience Provider'),
        ('venue_owner', 'Venue Owner'),
    )
    user_type = models.CharField(max_length=30, choices=USER_TYPES, default='regular')
    
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Host specific fields
    host_name = models.CharField(max_length=255, blank=True, null=True)
    host_bio = models.TextField(blank=True, null=True)
    host_profile_pic = models.ImageField(upload_to='host_profile_pics/', blank=True, null=True)
    host_designation = models.CharField(max_length=255, blank=True, null=True)
    host_location = models.CharField(max_length=255, blank=True, null=True)
    host_category = models.ForeignKey('HostCategory', on_delete=models.SET_NULL, null=True, blank=True)

    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(blank=True, null=True)
    is_verified_host = models.BooleanField(default=False)
    
    # Push Notifications
    fcm_token = models.CharField(max_length=500, blank=True, null=True)
    
    # Wallet
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Social
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    profile_likes = models.ManyToManyField('self', symmetrical=False, related_name='liked_profiles', blank=True)

    USERNAME_FIELD = 'phone_number'

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.phone_number if self.phone_number else self.email

class OTP(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.otp_code}"

class EventCategory(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    USER_TYPE_CHOICES = (
        ('artist', 'Artist'),
        ('event_organizer', 'Event Organizer'),
        ('experience_provider', 'Experience Provider'),
        ('venue_owner', 'Venue Owner'),
    )
    
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    allowed_user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, null=True, blank=True, help_text='Which user type can post in this category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class HostCategory(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    
    USER_TYPE_CHOICES = (
        ('artist', 'Artist'),
        ('event_organizer', 'Event Organizer'),
        ('experience_provider', 'Experience Provider'),
        ('venue_owner', 'Venue Owner'),
    )
    
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    allowed_user_type = models.CharField(max_length=30, choices=USER_TYPE_CHOICES, null=True, blank=True, help_text='Which user type belongs to this category')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class HostGalleryImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_gallery_images')
    image = models.ImageField(upload_to='host_gallery_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image for {self.user.full_name}"

class Event(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
        ('finished', 'Finished'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    location_url = models.URLField(max_length=500, blank=True, null=True)
    
    # Times
    event_date = models.DateField(null=True, blank=True)
    start_time = models.CharField(max_length=50, help_text="e.g. 24:00 - 12:00")
    duration = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 10 Min")
    
    description = models.TextField()
    booking_expiry_date = models.DateField(null=True, blank=True, help_text="Last date to book tickets")
    
    # Collaborators & Performers
    collaborator_invite = models.CharField(max_length=255, blank=True, null=True, help_text="Invite Collaborator info")
    artist_performer = models.CharField(max_length=255, blank=True, null=True)
    
    # Pricing & Capacity
    PAYMENT_TYPE_CHOICES = (
        ('free', 'Free'),
        ('own_payment', 'Own Payment'),
        ('pluuto_payments', 'Pluuto Payments'),
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='free')
    
    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_link = models.URLField(max_length=500, blank=True, null=True)
    
    maximum_capacity = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    
    # Files
    banner_image = models.ImageField(upload_to='event_banners/')
    terms_document = models.FileField(upload_to='event_docs/', blank=True, null=True)
    
    # Extra
    extra_text = models.TextField(blank=True, null=True, help_text="Add by text")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    # Control sensitive edits
    can_edit_sensitive_data = models.BooleanField(default=False, help_text="Admin control: Allow host to edit date, time, location, price")
    is_published = models.BooleanField(default=False, help_text="Only published events appear in the API")
    is_featured = models.BooleanField(default=False, help_text="Featured events appear on the home page")
    rejection_reason = models.TextField(blank=True, null=True)

    # Admin Payment Tracking
    ADMIN_PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )
    admin_payment_status = models.CharField(max_length=20, choices=ADMIN_PAYMENT_STATUS_CHOICES, default='pending')
    admin_payment_note = models.TextField(blank=True, null=True, help_text="Note regarding admin payment to host")
    
    # QR Code
    qr_code_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    # Rewards
    attendee_coins = models.PositiveIntegerField(default=0, help_text="Coins awarded for attending")
    scratch_prizes = models.TextField(blank=True, null=True, help_text="Comma separated list of prizes")
    
    # Social
    likes = models.ManyToManyField(User, related_name='liked_events', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorited_events', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.qr_code_token:
            self.qr_code_token = uuid.uuid4().hex
        
        super().save(*args, **kwargs)
        
        if not self.qr_code_image:
             qr = qrcode.QRCode(version=1, box_size=10, border=5)
             qr.add_data(self.qr_code_token)
             qr.make(fit=True)
             img = qr.make_image(fill_color="black", back_color="white")
             buffer = BytesIO()
             img.save(buffer, format="PNG")
             file_name = f'qr_{self.pk}.png'
             
             self.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=True)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    ticket_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    booking_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    # Guest Info
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_phone_number = models.CharField(max_length=15, blank=True, null=True)
    guest_country_code = models.CharField(max_length=5, blank=True, null=True)
    
    # Payment Info
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=50, blank=True, null=True)
    payment_source = models.CharField(max_length=50, blank=True, null=True, help_text="How payment was verified (e.g., 'api' or 'webhook')")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('pending_payment', 'Pending Payment'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    def save(self, *args, **kwargs):
        if not self.booking_code:
            # Generate code
            event_prefix = ''.join(c for c in self.event.title if c.isalnum())[:3].upper()
            if len(event_prefix) < 3:
                event_prefix = (event_prefix + 'EVT')[:3]
                
            for _ in range(5):
                 random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                 code = f"{event_prefix}-{random_str}"
                 if not Booking.objects.filter(booking_code=code).exists():
                     self.booking_code = code
                     break
            else:
                 # Fallback if collision persists (rare)
                 self.booking_code = f"{event_prefix}-{uuid.uuid4().hex[:6].upper()}"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.event.title}"

class EventPrize(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='prizes')
    prize_text = models.CharField(max_length=255)
    total_count = models.IntegerField(default=-1, help_text="-1 for unlimited")
    won_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        limit = 'unlimited' if self.total_count == -1 else self.total_count
        return f"{self.prize_text} ({self.won_count}/{limit})"

class ScratchPrize(models.Model):
    """Individual scratch prize configuration for an event"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='scratch_prize_items')
    image = models.ImageField(upload_to='scratch_prizes/', blank=True, null=True, help_text="Prize image")
    title = models.CharField(max_length=255, help_text="Prize title")
    description = models.TextField(blank=True, null=True, help_text="Prize description")
    code = models.CharField(max_length=100, blank=True, null=True, help_text="Prize code/coupon")
    is_better_luck = models.BooleanField(default=False, help_text="Is this a 'Better luck next time' prize?")
    total_count = models.IntegerField(default=-1, help_text="-1 for unlimited")
    won_count = models.IntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True, help_text="Expiry date for the prize")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        limit = 'unlimited' if self.total_count == -1 else self.total_count
        return f"{self.title} ({self.won_count}/{limit})"
    
    class Meta:
        ordering = ['-is_better_luck', 'created_at']  # Better luck items at the end

class ScratchCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scratch_cards')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    prize = models.ForeignKey('ScratchPrize', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_cards')
    prize_text = models.CharField(max_length=255)
    is_scratched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Card for {self.user.full_name} ({self.prize_text})"

class WalletTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wallet_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.full_name}: {self.amount}"

class EventGalleryImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='event_gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.event.title}"

class HostRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='host_requests')
    requested_type = models.CharField(max_length=30, choices=User.USER_TYPES)
    note = models.TextField(blank=True, null=True, help_text="Why do you want to become a host?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} request for {self.requested_type}"

class CollaborationRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='collaboration_requests')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_collaboration_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_collaboration_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'to_user')

    def __str__(self):
        return f"Collab: {self.from_user} -> {self.to_user} on {self.event}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, blank=True, null=True) # e.g. 'collaboration', 'event_approval'
    related_id = models.IntegerField(null=True, blank=True) # ID of related object (event_id, etc)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient}: {self.title}"

class EventEditHistory(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='edit_history')
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} - {self.field_name} changed"

class EventUpdateNotification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='update_notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_update_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.full_name} - {self.event.title}"

class AppFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.IntegerField(default=5)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.phone_number if self.user else 'Anonymous'} - Rating {self.rating}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
