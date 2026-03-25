from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, RegisterVerifyView, 
    LoginView, LoginVerifyView, 
    GoogleLoginView, LogoutAPIView,
    AppFeedbackCreateAPIView,
    EventCategoryListAPIView, EventCreateAPIView, 
    EventListAPIView, EventRetrieveUpdateAPIView, MyEventListAPIView, MyUpcomingEventsAPIView, MyPastEventsAPIView,
    UserUpcomingEventsAPIView, UserPastEventsAPIView,
    HostRequestCreateAPIView, HostCategoryListByTypeAPIView,
    BookingCreateAPIView, BookingListAPIView, AttendEventAPIView,
    ScratchCardListAPIView, ScratchCardRevealAPIView, WalletHistoryAPIView,
    LikeEventAPIView, UnlikeEventAPIView, ToggleFollowUserAPIView, ToggleLikeProfileAPIView, HostListAPIView, ActiveEventListAPIView,
    HomeAPIView, GlobalSearchAPIView, UserProfileView, ChangePasswordAPIView, SoftDeleteAccountAPIView, UserEventActionAPIView,
    AdminCreatedEventListAPIView, SendCollaborationRequestView, CollaborationRequestActionView, UserCollaborationRequestsView,
    HostEventBookingListAPIView, ArtistListAPIView, VenueListAPIView, ExperienceProviderListAPIView,
    HostDetailAPIView, HostGalleryManageView, EventBookingExportAPIView, EventSensitiveUpdateAPIView,
    UserEventUpdateNotificationListAPIView, CreateRazorpayOrderAPIView, VerifyRazorpayPaymentAPIView, RazorpayWebhookAPIView, RazorpayKeysAPIView, ToggleFavoriteEventAPIView,
    LikedEventsListAPIView, FavoritedEventsListAPIView, FollowingListAPIView, FollowersListAPIView, LikedProfilesListAPIView,
    NotificationListAPIView, NotificationMarkAllAsReadAPIView
)

urlpatterns = [
    # API Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/register/verify/', RegisterVerifyView.as_view(), name='register-verify'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/login/verify/', LoginVerifyView.as_view(), name='login-verify'),
    path('auth/google/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/password/change/', ChangePasswordAPIView.as_view(), name='password-change'),
    path('auth/account/delete/', SoftDeleteAccountAPIView.as_view(), name='account-delete'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Collaborations
    path('events/collaborate/', SendCollaborationRequestView.as_view(), name='event-collaborate'),
    path('collaborations/<int:pk>/action/', CollaborationRequestActionView.as_view(), name='collaboration-action'),
    path('collaborations/requests/', UserCollaborationRequestsView.as_view(), name='user-collaborations'),

    
    # Event APIs
    path('categories/', EventCategoryListAPIView.as_view(), name='category-list'),
    path('host-categories/', HostCategoryListByTypeAPIView.as_view(), name='host-category-list'),
    path('events/create/', EventCreateAPIView.as_view(), name='event-create'),
    path('events/', EventListAPIView.as_view(), name='event-list'),
    path('events/my/', MyEventListAPIView.as_view(), name='my-event-list'),
    path('events/my/upcoming/', MyUpcomingEventsAPIView.as_view(), name='my-upcoming-event-list'),
    path('events/my/past/', MyPastEventsAPIView.as_view(), name='my-past-event-list'),
    path('events/user/upcoming/', UserUpcomingEventsAPIView.as_view(), name='user-upcoming-event-list'), # New
    path('events/user/past/', UserPastEventsAPIView.as_view(), name='user-past-event-list'), # New

    path('events/admin-created/', AdminCreatedEventListAPIView.as_view(), name='admin-event-list'), # New Endpoint
    path('events/<int:pk>/', EventRetrieveUpdateAPIView.as_view(), name='event-detail'),
    path('events/<int:pk>/update-sensitive/', EventSensitiveUpdateAPIView.as_view(), name='event-update-sensitive'),
    path('events/<int:pk>/action/', UserEventActionAPIView.as_view(), name='event-action'),
    
    # New Features
    path('home/', HomeAPIView.as_view(), name='home-api'),
    path('search/', GlobalSearchAPIView.as_view(), name='global-search'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('host-requests/create/', HostRequestCreateAPIView.as_view(), name='host-request-create'),
    path('feedback/', AppFeedbackCreateAPIView.as_view(), name='app-feedback'),

    # User Feature APIs
    path('bookings/create/', BookingCreateAPIView.as_view(), name='booking-create'),
    path('bookings/', BookingListAPIView.as_view(), name='booking-list'),
    path('bookings/hosted/', HostEventBookingListAPIView.as_view(), name='host-booking-list'),
    path('events/<int:pk>/export_bookings/', EventBookingExportAPIView.as_view(), name='event-booking-export'),
    path('events/attend/', AttendEventAPIView.as_view(), name='event-attend'), # Scan QR
    path('notifications/', NotificationListAPIView.as_view(), name='notifications-list'),
    path('notifications/mark-all-read/', NotificationMarkAllAsReadAPIView.as_view(), name='notifications-mark-read'),
    path('notifications/event-updates/', UserEventUpdateNotificationListAPIView.as_view(), name='user-event-update-notifications'),
    path('bookings/create-razorpay-order/', CreateRazorpayOrderAPIView.as_view(), name='create-razorpay-order'),
    path('bookings/verify-razorpay-payment/', VerifyRazorpayPaymentAPIView.as_view(), name='verify-razorpay-payment'),
    path('bookings/razorpay-keys/', RazorpayKeysAPIView.as_view(), name='razorpay-keys'),
    path('webhook/razorpay/', RazorpayWebhookAPIView.as_view(), name='razorpay-webhook'),
    
    path('scratch-cards/', ScratchCardListAPIView.as_view(), name='scratch-card-list'),
    path('scratch-cards/<int:pk>/reveal/', ScratchCardRevealAPIView.as_view(), name='scratch-card-reveal'),
    
    path('wallet/history/', WalletHistoryAPIView.as_view(), name='wallet-history'),
    
    # Social Features
    path('events/<int:pk>/like/', LikeEventAPIView.as_view(), name='event-like'),
    path('events/<int:pk>/unlike/', UnlikeEventAPIView.as_view(), name='event-unlike'),
    path('events/<int:pk>/favorite/', ToggleFavoriteEventAPIView.as_view(), name='event-favorite-toggle'),
    path('users/<int:pk>/follow/', ToggleFollowUserAPIView.as_view(), name='user-follow'),
    path('users/<int:pk>/like/', ToggleLikeProfileAPIView.as_view(), name='user-like'),
    path('hosts/', HostListAPIView.as_view(), name='host-list'),
    path('hosts/<int:pk>/', HostDetailAPIView.as_view(), name='host-detail'),
    path('hosts/gallery/', HostGalleryManageView.as_view(), name='host-gallery-manage'),
    
    # New List APIs
    path('user/liked-events/', LikedEventsListAPIView.as_view(), name='user-liked-events'),
    path('user/favorited-events/', FavoritedEventsListAPIView.as_view(), name='user-favorited-events'),
    path('user/liked-profiles/', LikedProfilesListAPIView.as_view(), name='user-liked-profiles'),
    path('user/following/', FollowingListAPIView.as_view(), name='user-following'),
    path('user/followers/', FollowersListAPIView.as_view(), name='user-followers'),

    path('events/active/', ActiveEventListAPIView.as_view(), name='active-event-list'),
    path('artists/', ArtistListAPIView.as_view(), name='artist-list'),
    path('venues/', VenueListAPIView.as_view(), name='venue-list'),
    path('experients/', ExperienceProviderListAPIView.as_view(), name='experient-list'),
]
