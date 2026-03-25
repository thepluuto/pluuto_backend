from rest_framework import serializers
from .models import User, Event, EventCategory, EventGalleryImage, HostRequest, Booking, ScratchCard, WalletTransaction, CollaborationRequest, HostGalleryImage, HostCategory, EventUpdateNotification, Notification, AppFeedback
from django.db.models import Sum

# ... (skipped imports)



from django.contrib.auth import authenticate

class HostCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = HostCategory
        fields = ['id', 'name', 'details', 'status', 'allowed_user_type']

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    is_following = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='liked_profiles.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    host_category_details = HostCategorySerializer(source='host_category', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'country_code', 'full_name', 'email', 'user_type', 'is_active', 'date_joined', 
                  'followers_count', 'following_count', 'is_following', 'likes_count', 'is_liked', 'profile_pic',
                  'host_name', 'host_bio', 'host_designation', 'host_profile_pic', 'host_category', 'host_category_details', 'host_location', 'is_verified_host']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.id).exists()
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if request.user has liked obj (obj is in request.user.profile_likes)
            # No, 'profile_likes' is ManyToMany on User.
            # If User A likes User B: A.profile_likes.add(B)
            # So B.liked_profiles.filter(id=A.id).exists()? No.
            # 'profile_likes' related_name is 'liked_profiles'.
            # If A.profile_likes.add(B):
            # A has B in profile_likes.
            # B has A in liked_profiles.
            
            # We want to know if "request.user likes obj".
            # So is obj in request.user.profile_likes?
            return request.user.profile_likes.filter(id=obj.id).exists()
        return False



class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    events_attended_count = serializers.SerializerMethodField()
    host_request_status = serializers.SerializerMethodField()
    host_category_details = HostCategorySerializer(source='host_category', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'country_code', 'full_name', 'email', 'user_type', 'is_active', 'date_joined', 
                  'followers_count', 'following_count', 'wallet_balance', 'profile_pic', 'events_attended_count', 'auth_provider',
                  'host_name', 'host_bio', 'host_profile_pic', 'host_location', 'host_request_status', 'host_designation', 'host_category', 'host_category_details', 'is_verified_host']
        read_only_fields = ['phone_number', 'country_code', 'user_type', 'is_active', 'date_joined', 'wallet_balance', 'auth_provider', 'host_category_details', 'is_verified_host']

    def get_events_attended_count(self, obj):
        return obj.bookings.filter(status='attended').count()

    def get_host_request_status(self, obj):
        if obj.user_type != 'regular':
             return 'approved'
        last_req = obj.host_requests.order_by('-created_at').first()
        if last_req:
             return last_req.status
        return 'not_send'

class HostGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostGalleryImage
        fields = ['id', 'image', 'created_at']

class UserHostDetailSerializer(UserSerializer):
    host_gallery = HostGalleryImageSerializer(source='host_gallery_images', many=True, read_only=True)
    posted_events_count = serializers.SerializerMethodField()
    host_category_details = HostCategorySerializer(source='host_category', read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['host_gallery', 'host_bio', 'host_designation', 'posted_events_count', 'host_category', 'host_category_details']
        
    def get_posted_events_count(self, obj):
        return obj.events.filter(status='approved').count()
class RegisterRequestSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)
    country_code = serializers.CharField(max_length=5, required=False, allow_blank=True)
    email = serializers.EmailField()

class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    country_code = serializers.CharField(max_length=5, required=False, allow_blank=True)

class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    country_code = serializers.CharField(max_length=5, required=False, allow_blank=True)
    otp_code = serializers.CharField(max_length=6)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

class GoogleLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField()

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = ['id', 'name', 'details', 'status', 'allowed_user_type', 'created_at']

class EventGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventGalleryImage
        fields = ['id', 'image', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    gallery_images = EventGalleryImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True, required=False
    )
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    owner_host_name = serializers.CharField(source='owner.host_name', read_only=True)
    owner_host_designation = serializers.CharField(source='owner.host_designation', read_only=True)
    owner_profile_pic = serializers.ImageField(source='owner.host_profile_pic', read_only=True)
    owner_is_following = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    collaborators = serializers.SerializerMethodField()
    
    # Booking Details
    total_booking_count = serializers.IntegerField(source='maximum_capacity', read_only=True)
    booked_count = serializers.SerializerMethodField()
    attended_count = serializers.SerializerMethodField()
    total_booked_amount = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()
    can_book = serializers.SerializerMethodField()
    total_bookings_count = serializers.SerializerMethodField()
    total_bookings_count = serializers.SerializerMethodField()
    recent_attendees = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_booked = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'owner', 'owner_name', 'owner_host_name', 'owner_host_designation', 'owner_profile_pic', 'owner_is_following', 'category', 'category_name', 'title', 'location', 'location_url',
            'event_date', 'start_time', 'duration', 'description', 'booking_expiry_date', 'collaborator_invite', 
            'artist_performer', 'payment_type', 'maximum_capacity', 'regular_price', 'offer_price', 'payment_link', 
            'banner_image', 'terms_document', 'extra_text', 'status', 'gallery_images', 'uploaded_images',
            'likes_count', 'is_liked', 'collaborators',
            'total_booking_count', 'booked_count', 'available_count', 'can_book',
            'can_edit_sensitive_data', 'total_bookings_count', 'is_booked',
            'attended_count', 'total_booked_amount', 'admin_payment_status', 'admin_payment_note', 'recent_attendees', 'is_favorited'
        ]
        read_only_fields = ['owner', 'status', 'gallery_images', 'likes_count', 'can_edit_sensitive_data', 'admin_payment_status', 'admin_payment_note']

    def get_is_booked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookings.filter(user=request.user, status__in=['booked', 'attended']).exists()
        return False



    def get_collaborators(self, obj):
        requests = obj.collaboration_requests.filter(status='accepted')
        return UserSerializer([r.to_user for r in requests], many=True).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_owner_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.following.filter(id=obj.owner.id).exists()
        return False

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        event = Event.objects.create(**validated_data)
        
        for image in uploaded_images:
            EventGalleryImage.objects.create(event=event, image=image)
        
        return event

    def validate(self, data):
        # Removed user category validation for now.
        
        # Booking Expiry Validation
        booking_expiry_date = data.get('booking_expiry_date')
        event_date = data.get('event_date')
        
        if self.instance:
            if not booking_expiry_date:
                booking_expiry_date = self.instance.booking_expiry_date
            if not event_date:
                event_date = self.instance.event_date

        if booking_expiry_date and event_date:
             if booking_expiry_date > event_date:
                 raise serializers.ValidationError({"booking_expiry_date": "Booking expiry date must be on or before the event date."})
        
        return data

    def get_booked_count(self, obj):
        total_tickets = obj.bookings.filter(status__in=['booked', 'attended']).aggregate(Sum('ticket_count'))['ticket_count__sum']
        return total_tickets or 0

    def get_attended_count(self, obj):
        total_tickets = obj.bookings.filter(status='attended').aggregate(Sum('ticket_count'))['ticket_count__sum']
        return total_tickets or 0

    def get_total_booked_amount(self, obj):
        total_amount = obj.bookings.filter(status__in=['booked', 'attended']).aggregate(Sum('total_price'))['total_price__sum']
        return total_amount or 0

    def get_total_bookings_count(self, obj):
        return obj.bookings.filter(status__in=['booked', 'attended']).count()

    def get_available_count(self, obj):
        if obj.maximum_capacity:
             booked = self.get_booked_count(obj)
             return max(0, obj.maximum_capacity - booked)
        return None

    def get_can_book(self, obj):
         if obj.status != 'approved':
             return False

         if obj.payment_type != 'pluuto_payments':
             return False
        
         if obj.maximum_capacity:
             available = self.get_available_count(obj)
             if available <= 0:
                 return False
         
         if obj.booking_expiry_date:
             from django.utils import timezone
             if timezone.now().date() > obj.booking_expiry_date:
                 return False
         
         if obj.event_date:
             from django.utils import timezone
             if timezone.now().date() > obj.event_date:
                 return False
         
         return True

    def get_recent_attendees(self, obj):
        bookings = obj.bookings.filter(status__in=['booked', 'attended']).order_by('-booking_date').select_related('user')[:3]
        result = []
        for booking in bookings:
            user = booking.user
            profile_pic_url = None
            if user.profile_pic:
                try:
                    request = self.context.get('request')
                    if request:
                        profile_pic_url = request.build_absolute_uri(user.profile_pic.url)
                    else:
                        profile_pic_url = user.profile_pic.url
                except Exception:
                     profile_pic_url = user.profile_pic.url if user.profile_pic else None
            
            result.append({
                'full_name': user.full_name,
                'profile_pic': profile_pic_url
            })
        return result

class EventSensitiveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['event_date', 'start_time', 'duration', 'booking_expiry_date', 'location', 'location_url', 'regular_price', 'offer_price']

class HostRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostRequest
        fields = ['id', 'requested_type', 'note', 'status', 'created_at']


        read_only_fields = ['status', 'created_at']
    
    def validate_requested_type(self, value):
        if value not in dict(User.USER_TYPES):
            raise serializers.ValidationError("Invalid user type.")
        if value == 'regular':
             raise serializers.ValidationError("You cannot request to become a regular user.")
        return value

class BookingSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_location = serializers.CharField(source='event.location', read_only=True)
    event_start_time = serializers.CharField(source='event.start_time', read_only=True)
    event_banner = serializers.ImageField(source='event.banner_image', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'event', 'event_title', 'event_location', 'event_start_time', 'event_banner',
                  'ticket_count', 'total_price', 'booking_date', 'booking_code', 'status',
                  'payment_id', 'transaction_id', 'payment_status', 'paid_amount', 'paid_at',
                  'guest_name', 'guest_email', 'guest_phone_number', 'guest_country_code']
        read_only_fields = ['total_price', 'booking_date', 'booking_code', 'status', 'payment_status']

class HostBookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_profile_pic = serializers.ImageField(source='user.profile_pic', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'event', 'event_title', 'user_name', 'user_email', 'user_phone', 'user_profile_pic',
                  'ticket_count', 'total_price', 'booking_date', 'booking_code', 'status',
                  'guest_name', 'guest_email', 'guest_phone_number', 'guest_country_code']
        extra_kwargs = {
            'payment_id': {'write_only': True, 'required': False},
            'transaction_id': {'write_only': True, 'required': False}
        }

class ScratchCardSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    expiry_date = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_better_luck = serializers.SerializerMethodField()

    class Meta:
        model = ScratchCard
        fields = ['id', 'event', 'event_title', 'prize_text', 'is_scratched', 'created_at', 'expiry_date', 'is_expired', 'is_better_luck']
        read_only_fields = ['event', 'prize_text', 'created_at']
    
    def get_expiry_date(self, obj):
        """Get expiry date from the associated prize"""
        if hasattr(obj, 'prize') and obj.prize and obj.prize.expiry_date:
            return obj.prize.expiry_date.strftime('%Y-%m-%d')
        return None
    
    def get_is_expired(self, obj):
        """Check if the prize has expired"""
        if hasattr(obj, 'prize') and obj.prize and obj.prize.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > obj.prize.expiry_date
        return False

    def get_is_better_luck(self, obj):
        """Check if the prize is a 'better luck next time' type"""
        if hasattr(obj, 'prize') and obj.prize:
            return obj.prize.is_better_luck
        return False

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['id', 'amount', 'description', 'created_at']

class CollaborationRequestSerializer(serializers.ModelSerializer):
    from_user_details = UserSerializer(source='from_user', read_only=True)
    to_user_details = UserSerializer(source='to_user', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = CollaborationRequest
        fields = ['id', 'event', 'event_title', 'from_user', 'from_user_details', 'to_user', 'to_user_details', 'status', 'created_at']
        read_only_fields = ['from_user', 'status', 'created_at']

class EventUpdateNotificationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    class Meta:
        model = EventUpdateNotification
        fields = ['id', 'event', 'event_title', 'message', 'is_read', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'notification_type', 'related_id', 'created_at']

class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        fields = ['id', 'user', 'rating', 'text', 'created_at']
        read_only_fields = ['user']
