from django.urls import path
from .views import (
    AdminLoginView, AdminLogoutView, AdminDashboardView,
    AdminUserListView, AdminUserDetailView, AdminUserPromoteView,
    AdminUserBlockView, AdminUserUnblockView, AdminHostVerifyView, AdminHostUnverifyView,
    AdminProfileEditView, AdminPasswordChangeView,
    AdminCategoryListView, AdminCategoryCreateView,
    AdminCategoryUpdateView, AdminCategoryDeleteView,
    AdminHostCategoryListView, AdminHostCategoryCreateView,
    AdminHostCategoryUpdateView, AdminHostCategoryDeleteView,
    AdminEventListView, AdminEventDetailView,
    AdminEventApproveView, AdminEventRejectView, AdminEventCreateView,
    AdminEventBlockView, AdminEventUnblockView, AdminEventUpdateRewardsView, AdminEventUpdateView, AdminEventFinishView,
    AdminEventToggleFeaturedView, AdminEventToggleSensitiveEditView, AdminEventUpdatePaymentStatusView,
    AdminHostRequestListView, AdminHostRequestDetailView,
    AdminHostRequestApproveView, AdminHostRequestRejectView,
    AdminBookingListView, AdminScanResultListView, AdminBookingExportView, AdminEventGalleryImageDeleteView,
    AdminAppFeedbackListView,
    AdminContactMessageListView, AdminContactMessageDeleteView
)

urlpatterns = [
    # Custom Admin Panel
    path('', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('login/', AdminLoginView.as_view(), name='admin_login'),
    path('logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('users/<int:pk>/promote/', AdminUserPromoteView.as_view(), name='admin_user_promote'),
    path('users/<int:pk>/block/', AdminUserBlockView.as_view(), name='admin_user_block'),
    path('users/<int:pk>/unblock/', AdminUserUnblockView.as_view(), name='admin_user_unblock'),
    path('users/<int:pk>/verify/', AdminHostVerifyView.as_view(), name='admin_host_verify'),
    path('users/<int:pk>/unverify/', AdminHostUnverifyView.as_view(), name='admin_host_unverify'),
    path('profile/', AdminProfileEditView.as_view(), name='admin_profile_edit'),
    path('profile/password/', AdminPasswordChangeView.as_view(), name='admin_change_password'),
    
    # Event Categories
    path('categories/', AdminCategoryListView.as_view(), name='admin_category_list'),
    path('categories/add/', AdminCategoryCreateView.as_view(), name='admin_category_add'),
    path('categories/<int:pk>/edit/', AdminCategoryUpdateView.as_view(), name='admin_category_edit'),
    path('categories/<int:pk>/delete/', AdminCategoryDeleteView.as_view(), name='admin_category_delete'),
    
    # Host Categories
    path('host-categories/', AdminHostCategoryListView.as_view(), name='admin_host_category_list'),
    path('host-categories/add/', AdminHostCategoryCreateView.as_view(), name='admin_host_category_add'),
    path('host-categories/<int:pk>/edit/', AdminHostCategoryUpdateView.as_view(), name='admin_host_category_edit'),
    path('host-categories/<int:pk>/delete/', AdminHostCategoryDeleteView.as_view(), name='admin_host_category_delete'),
    
    # Events Management
    path('events/', AdminEventListView.as_view(), name='admin_event_list'),
    path('events/create/', AdminEventCreateView.as_view(), name='admin_event_create'),
    path('events/<int:pk>/', AdminEventDetailView.as_view(), name='admin_event_detail'),
    path('events/<int:pk>/update-payment/', AdminEventUpdatePaymentStatusView.as_view(), name='admin_event_update_payment'),
    path('events/<int:pk>/approve/', AdminEventApproveView.as_view(), name='admin_event_approve'),
    path('events/<int:pk>/reject/', AdminEventRejectView.as_view(), name='admin_event_reject'),
    path('events/<int:pk>/block/', AdminEventBlockView.as_view(), name='admin_event_block'),
    path('events/<int:pk>/unblock/', AdminEventUnblockView.as_view(), name='admin_event_unblock'),
    path('events/<int:pk>/finish/', AdminEventFinishView.as_view(), name='admin_event_finish'),
    path('events/<int:pk>/edit/', AdminEventUpdateView.as_view(), name='admin_event_edit'),
    path('events/<int:pk>/update-rewards/', AdminEventUpdateRewardsView.as_view(), name='admin_event_update_rewards'),
    path('events/<int:pk>/update-rewards/', AdminEventUpdateRewardsView.as_view(), name='admin_event_update_rewards'),
    path('events/<int:pk>/toggle-featured/', AdminEventToggleFeaturedView.as_view(), name='admin_event_toggle_featured'),
    path('events/<int:pk>/toggle-sensitive-edit/', AdminEventToggleSensitiveEditView.as_view(), name='admin_event_toggle_sensitive_edit'),
    
    # Host Requests
    path('host-requests/', AdminHostRequestListView.as_view(), name='admin_host_request_list'),
    path('host-requests/<int:pk>/', AdminHostRequestDetailView.as_view(), name='admin_host_request_detail'),
    path('host-requests/<int:pk>/approve/', AdminHostRequestApproveView.as_view(), name='admin_host_request_approve'),
    path('host-requests/<int:pk>/reject/', AdminHostRequestRejectView.as_view(), name='admin_host_request_reject'),
    
    # Bookings
    path('bookings/export/', AdminBookingExportView.as_view(), name='admin_booking_export'),
    path('bookings/', AdminBookingListView.as_view(), name='admin_booking_list'),

    # Scan Results
    path('scan-results/', AdminScanResultListView.as_view(), name='admin_scan_result_list'),
    
    # Gallery
    path('gallery-images/<int:pk>/delete/', AdminEventGalleryImageDeleteView.as_view(), name='admin_gallery_image_delete'),

    # Feedback
    path('feedback/', AdminAppFeedbackListView.as_view(), name='admin_app_feedback_list'),

    # Contact Messages
    path('contact-messages/', AdminContactMessageListView.as_view(), name='admin_contact_message_list'),
    path('contact-messages/<int:pk>/delete/', AdminContactMessageDeleteView.as_view(), name='admin_contact_message_delete'),
]
