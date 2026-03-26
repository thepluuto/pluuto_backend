from rest_framework.views import APIView
from rest_framework import status
import razorpay
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from .models import User, Event, EventCategory, EventGalleryImage, OTP, HostRequest, Booking, ScratchPrize, ScratchCard, WalletTransaction, CollaborationRequest, HostGalleryImage, HostCategory, Notification, AppFeedback
from django.db import models
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterRequestSerializer, LoginRequestSerializer,
    OTPVerifySerializer, GoogleLoginSerializer,
    EventSerializer, EventCategorySerializer, HostRequestSerializer,
    BookingSerializer, ScratchCardSerializer, WalletTransactionSerializer, CollaborationRequestSerializer,
    HostBookingSerializer,
    HostBookingSerializer,
    UserHostDetailSerializer, HostGalleryImageSerializer, HostCategorySerializer,
    EventSensitiveUpdateSerializer, EventUpdateNotificationSerializer, NotificationSerializer
)
from rest_framework import permissions, generics, serializers
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Count, Q, F, Sum
from django.utils import timezone

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid
from .utils import api_response, generate_event_qr
from django.contrib.auth import login, logout
import datetime
from rest_framework_simplejwt.tokens import RefreshToken
import random
import requests
from django.views import View
from rest_framework import filters
# Admin Imports
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
import datetime
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from .forms import EventCreateForm
import csv

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.validated_data['full_name']
            phone_number = serializer.validated_data['phone_number']
            country_code = serializer.validated_data.get('country_code', '')
            email = serializer.validated_data['email']

            if User.objects.filter(phone_number=phone_number, country_code=country_code).exists():
                return api_response('error', 'User with this phone number already exists', status_code=400)
                
            if User.objects.filter(email=email).exists():
                return api_response('error', 'User with this email already exists', status_code=400)

            # Generate and Send OTP (Mock for now)
            otp_code = '123456' # For testing purpose
            OTP.objects.create(phone_number=phone_number, otp_code=otp_code)
            
            # In production, integrate SMS API here
            print(f"OTP for {phone_number}: {otp_code}")

            return api_response('success', 'OTP sent successfully', {'otp_sent_to': phone_number, 'otp': otp_code})
        
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class RegisterVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            country_code = serializer.validated_data.get('country_code', '')
            otp_code = serializer.validated_data['otp_code']
            
            # Get full_name and email from validated data (sent by client again)
            full_name = serializer.validated_data.get('full_name') or request.data.get('full_name')
            email = serializer.validated_data.get('email') or request.data.get('email')

            try:
                otp_record = OTP.objects.get(phone_number=phone_number, otp_code=otp_code, is_verified=False)
                # Verify OTP logic (time expiry check can be added)
                otp_record.is_verified = True
                otp_record.save()
                
                # Double check uniqueness before creation (race condition check)
                if User.objects.filter(email=email).exists():
                     return api_response('error', 'User with this email already exists', status_code=400)
                     
                user = User.objects.create_user(phone_number=phone_number, full_name=full_name, email=email)
                if country_code:
                    user.country_code = country_code
                    user.save()
                
                fcm_token = request.data.get('fcm_token')
                if fcm_token:
                    user.fcm_token = fcm_token
                    user.save()
                
                tokens = get_tokens_for_user(user)
                return api_response('success', 'Account created successfully', {
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                })

            except OTP.DoesNotExist:
                return api_response('error', 'Invalid OTP or Phone Number', status_code=400)
        
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            country_code = serializer.validated_data.get('country_code', '')
            
            if not User.objects.filter(phone_number=phone_number, country_code=country_code).exists():
                return api_response('error', 'User not found. Please register.', status_code=404)

            otp_code = '123456' # For testing purpose
            OTP.objects.create(phone_number=phone_number, otp_code=otp_code)
            print(f"OTP for {phone_number}: {otp_code}")

            return api_response('success', 'OTP sent successfully', {'otp_sent_to': phone_number, 'otp': otp_code})
        
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class LoginVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            country_code = serializer.validated_data.get('country_code', '')
            otp_code = serializer.validated_data['otp_code']

            try:
                otp_record = OTP.objects.get(phone_number=phone_number, otp_code=otp_code, is_verified=False)
                otp_record.is_verified = True
                otp_record.save()

                user = User.objects.get(phone_number=phone_number, country_code=country_code)
                
                # Check if user is blocked
                if user.is_blocked:
                    return api_response('error', f'Your account has been blocked. Reason: {user.block_reason}', status_code=403)
                
                fcm_token = request.data.get('fcm_token')
                if fcm_token:
                    user.fcm_token = fcm_token
                    user.save()
                
                tokens = get_tokens_for_user(user)
                
                return api_response('success', 'Login successful', {
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                })

            except OTP.DoesNotExist:
                return api_response('error', 'Invalid OTP or Phone Number', status_code=400)
            except User.DoesNotExist:
                 return api_response('error', 'User not found', status_code=404)

        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class GoogleLoginView(APIView):
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        if serializer.is_valid():
            input_token = serializer.validated_data['access_token']
            email = None
            name = None
            phone_number = None
            
            # 1. Try Validating as ID Token (JWT)
            try:
                # Google ID Token validation endpoint
                id_token_response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={'id_token': input_token})
                if id_token_response.status_code == 200:
                    data = id_token_response.json()
                    email = data.get('email')
                    name = data.get('name')
                    phone_number = data.get('phone_number') # Usually not present, but good to check
            except Exception as e:
                print(f"ID Token check failed: {e}")
            
            # 2. If valid ID Token not found, Try Validating as Access Token
            if not email:
                try:
                    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                    response = requests.get(user_info_url, params={'access_token': input_token})
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        email = user_data.get('email')
                        name = user_data.get('name')
                        phone_number = user_data.get('phone_number')
                except Exception as e:
                    print(f"Access Token check failed: {e}")
            
            if not email:
                return api_response('error', 'Invalid Google Token. Please provide a valid Access Token or ID Token.', status_code=400)
                
            # Check if user exists
            try:
                user = User.objects.get(email=email)
                
                # User exists - Generate tokens
                tokens = get_tokens_for_user(user)
                return api_response('success', 'Google Login successful', {
                    'user': UserSerializer(user).data,
                    'tokens': tokens
                })
                
            except User.DoesNotExist:
                # User does not exist - Return empty token and user info for registration
                return api_response('success', 'User does not exist', {
                    'tokens': '',
                    'email': email,
                    'full_name': name,
                    'phone_number': phone_number
                })
        
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

# --------------------------
# Admin Panel Views
# --------------------------

class AdminLoginView(DjangoLoginView):
    template_name = 'events/admin/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('admin_dashboard')

class AdminLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('admin_login')

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'events/admin/dashboard.html'
    login_url = 'admin_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        
        # 1. Dashboard Boxes Data
        context['total_users'] = User.objects.count()
        context['upcoming_events_count'] = Event.objects.filter(status='approved', event_date__gte=today).count()
        context['approval_pending_events_count'] = Event.objects.filter(status='pending').count()
        context['pending_host_requests_count'] = HostRequest.objects.filter(status='pending').count()
        
        # 2. Bottom Lists
        # Left Side: Today's Events
        context['todays_events'] = Event.objects.filter(event_date=today).order_by('created_at')
        
        # Right Side: Expired but finishing pending event list
        # Events that are approved (or unfinished) but date has passed
        context['expired_pending_finish_events'] = Event.objects.filter(status='approved', event_date__lt=today).order_by('-event_date')

        # Recent Data (Restoring)
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_host_requests'] = HostRequest.objects.filter(status='pending').order_by('-created_at')[:5]
        context['pending_host_requests'] = HostRequest.objects.filter(status='pending').count() # Needed for sidebar logic
        context['pending_events'] = Event.objects.filter(status='pending').count() # Needed for sidebar logic

        # Graph Data (Last 7 Days)
        days = []
        graph_users = []
        graph_bookings = []
        
        for i in range(6, -1, -1):
            d = today - datetime.timedelta(days=i)
            day_str = d.strftime('%b %d')
            days.append(day_str)
            graph_users.append(User.objects.filter(date_joined__date=d).count())
            graph_bookings.append(Booking.objects.filter(booking_date__date=d).count())
            
        context['graph_labels'] = days
        context['graph_users_data'] = graph_users
        context['graph_bookings_data'] = graph_bookings
        
        return context

class AdminUserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'events/admin/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    ordering = ['-date_joined']
    login_url = 'admin_login'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(phone_number__icontains=search) |
                Q(email__icontains=search)
            )
        
        # User type filter
        user_type = self.request.GET.get('user_type', '')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Auth provider filter
        auth_provider = self.request.GET.get('auth_provider', '')
        if auth_provider:
            queryset = queryset.filter(auth_provider=auth_provider)
        
        # Status filter
        is_active = self.request.GET.get('is_active', '')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass Active Host Categories for the promotion modal
        # We'll use this in JS to filter by allowed_user_type
        # Let's pass simple dict list
        categories = HostCategory.objects.filter(status='active').values('id', 'name', 'allowed_user_type')
        context['host_categories_json'] = list(categories) 
        return context

class AdminUserPromoteView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        # Get data from POST
        new_user_type = request.POST.get('user_type')
        host_category_id = request.POST.get('host_category')
        
        if not new_user_type:
            messages.error(request, 'Please select a user type.')
            # Safe redirect
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('admin_user_list')
            
        # Basic validation
        if new_user_type not in dict(User.USER_TYPES):
            messages.error(request, 'Invalid user type selected.')
            return redirect('admin_user_list')
            
        # Handle regular user (demotion or just switch) - no category needed
        if new_user_type == 'regular':
            user.user_type = new_user_type
            user.host_category = None 
            user.save()
            messages.success(request, f'User {user.full_name} demoted to Regular User.')
            return redirect('admin_user_list')
            
        # Handle host types - check category
        if host_category_id:
             try:
                 category = HostCategory.objects.get(pk=host_category_id)
                 user.host_category = category
             except HostCategory.DoesNotExist:
                 messages.warning(request, 'Selected Host Category invalid. User promoted without category.')
        
        user.user_type = new_user_type
        user.save()
        
        cat_msg = f" in category {user.host_category.name}" if user.host_category else ""
        messages.success(request, f'User {user.full_name} promoted to {user.get_user_type_display()}{cat_msg}.')
        return redirect('admin_user_list')
        
class AdminUserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'events/admin/user_detail.html'
    context_object_name = 'object'
    login_url = 'admin_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_events'] = Event.objects.filter(owner=self.object).order_by('-created_at')
        return context

class AdminUserPromoteView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user_type = request.POST.get('user_type')
        
        if user_type in dict(User.USER_TYPES):
            user.user_type = user_type
            user.save()
            messages.success(request, f'User {user.full_name} has been promoted to {user.get_user_type_display()}.')
        else:
            messages.error(request, 'Invalid user type selected.')
        
        return HttpResponseRedirect(reverse_lazy('admin_user_list'))

class AdminUserBlockView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        block_reason = request.POST.get('block_reason', '')
        
        if not block_reason:
            messages.error(request, 'Block reason is required.')
            return HttpResponseRedirect(reverse_lazy('admin_user_detail', kwargs={'pk': pk}))
        
        user.is_blocked = True
        user.block_reason = block_reason
        user.is_active = False  # Also deactivate the user
        user.save()
        
        messages.success(request, f'User {user.full_name} has been blocked.')
        return HttpResponseRedirect(reverse_lazy('admin_user_detail', kwargs={'pk': pk}))

class AdminUserUnblockView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        user.is_blocked = False
        user.block_reason = None
        user.is_active = True  # Reactivate the user
        user.save()
        
        messages.success(request, f'User {user.full_name} has been unblocked.')
        return HttpResponseRedirect(reverse_lazy('admin_user_detail', kwargs={'pk': pk}))

class AdminHostVerifyView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_verified_host = True
        user.save()
        
        Notification.objects.create(
            recipient=user,
            title="Host Profile Verified",
            message=f"Congratulations! Your host profile '{user.full_name}' was verified.",
            notification_type="host_verification",
            related_id=user.id
        )
        
        messages.success(request, f'Host {user.full_name} has been verified.')
        return HttpResponseRedirect(reverse_lazy('admin_user_detail', kwargs={'pk': pk}))

class AdminHostUnverifyView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_verified_host = False
        user.save()
        messages.success(request, f'Host {user.full_name} has been unverified.')
        return HttpResponseRedirect(reverse_lazy('admin_user_detail', kwargs={'pk': pk}))

class AdminProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['full_name', 'email']
    template_name = 'events/admin/profile_edit.html'
    success_url = reverse_lazy('admin_profile_edit')
    login_url = 'admin_login'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

class AdminPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'events/admin/change_password.html'
    success_url = reverse_lazy('admin_profile_edit')
    login_url = 'admin_login'
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)

# --------------------------
# Event Category Views
# --------------------------

class AdminCategoryListView(LoginRequiredMixin, ListView):
    model = EventCategory
    template_name = 'events/admin/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    ordering = ['-created_at']
    login_url = 'admin_login'

class AdminCategoryCreateView(LoginRequiredMixin, CreateView):
    model = EventCategory
    fields = ['name', 'details', 'status', 'allowed_user_type']
    template_name = 'events/admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')
    login_url = 'admin_login'

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)

class AdminCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = EventCategory
    fields = ['name', 'details', 'status', 'allowed_user_type']
    template_name = 'events/admin/category_form.html'
    success_url = reverse_lazy('admin_category_list')
    login_url = 'admin_login'

class AdminUserPromoteView(LoginRequiredMixin, View):
    login_url = 'admin_login'
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        
        # Get data from POST
        new_user_type = request.POST.get('user_type')
        host_category_id = request.POST.get('host_category')
        
        if not new_user_type:
            messages.error(request, 'Please select a user type.')
            return redirect('admin_user_list')
            
        # Basic validation
        if new_user_type not in dict(User.USER_TYPES):
            messages.error(request, 'Invalid user type selected.')
            return redirect('admin_user_list')
            
        # Handle regular user (demotion or just switch) - no category needed
        if new_user_type == 'regular':
            user.user_type = new_user_type
            user.host_category = None
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, f'User {user.full_name|default:"User"} demoted to Regular User.')
            return redirect('admin_user_list')
            
        # Handle admin user
        if new_user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
            if not user.full_name or user.full_name == '-':
                user.full_name = 'Administrator'
            user.set_password('admin@123')
            user.host_category = None
        else:
            # Handle other host types
            user.is_staff = False
            user.is_superuser = False
            if host_category_id:
                 try:
                     category = HostCategory.objects.get(pk=host_category_id)
                     user.host_category = category
                 except HostCategory.DoesNotExist:
                     messages.warning(request, 'Selected Host Category invalid. User promoted without category.')
        
        user.user_type = new_user_type
        user.save()
        
        cat_msg = f" in category {user.host_category.name}" if user.host_category else ""
        messages.success(request, f'User {user.full_name|default:"Administrator"} promoted to {user.get_user_type_display()}{cat_msg}.')
        return redirect('admin_user_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)

class AdminCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = EventCategory
    template_name = 'events/admin/category_confirm_delete.html'
    success_url = reverse_lazy('admin_category_list')
    login_url = 'admin_login'

# Host Categories
class AdminHostCategoryListView(LoginRequiredMixin, ListView):
    model = HostCategory
    template_name = 'events/admin/host_category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    ordering = ['-created_at']
    login_url = 'admin_login'

class AdminHostCategoryCreateView(LoginRequiredMixin, CreateView):
    model = HostCategory
    fields = ['name', 'details', 'status', 'allowed_user_type']
    template_name = 'events/admin/host_category_form.html'
    success_url = reverse_lazy('admin_host_category_list')
    login_url = 'admin_login'

    def form_valid(self, form):
        messages.success(self.request, 'Host Category created successfully.')
        return super().form_valid(form)

class AdminHostCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = HostCategory
    fields = ['name', 'details', 'status', 'allowed_user_type']
    template_name = 'events/admin/host_category_form.html'
    success_url = reverse_lazy('admin_host_category_list')
    login_url = 'admin_login'

    def form_valid(self, form):
        messages.success(self.request, 'Host Category updated successfully.')
        return super().form_valid(form)

class AdminHostCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = HostCategory
    template_name = 'events/admin/host_category_confirm_delete.html'
    success_url = reverse_lazy('admin_host_category_list')
    login_url = 'admin_login'


# --------------------------
# Event API Views
# --------------------------

class EventCategoryListAPIView(generics.ListAPIView):
    queryset = EventCategory.objects.filter(status='active')
    serializer_class = EventCategorySerializer
    permission_classes = [permissions.AllowAny]

class EventCreateAPIView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # The serializer handles creation, we just pass the owner
        serializer.save(owner=self.request.user)

class EventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()
        queryset = Event.objects.filter(status='approved', event_date__gte=today).order_by('-created_at')

        # If user wants to see their own events (Legacy support, though MyEventList exists)
        if self.request.query_params.get('my_events') == 'true' and user.is_authenticated:
            queryset = Event.objects.filter(owner=user).order_by('-created_at')
        
        # Search Filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(location__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Category Filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        # Date Filter
        date_param = self.request.query_params.get('date')
        if date_param:
            try:
                queryset = queryset.filter(event_date=date_param)
            except ValueError:
                pass

        # Month Filter
        month_param_raw = self.request.query_params.get('month')
        year_param = self.request.query_params.get('year')
        if month_param_raw:
            try:
                if '-' in month_param_raw:
                    y, m = month_param_raw.split('-')
                    queryset = queryset.filter(event_date__year=int(y), event_date__month=int(m))
                else:
                    m = int(month_param_raw)
                    y = int(year_param) if year_param else timezone.now().year
                    queryset = queryset.filter(event_date__year=y, event_date__month=m)
            except ValueError:
                pass

        return queryset

class MyEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        queryset = Event.objects.filter(owner=self.request.user).order_by('-created_at')

        # Search Filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(location__icontains=search) | 
                Q(description__icontains=search)
            )

        # Category Filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

class EventRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Allow viewing if owner OR if approved
        if self.request.method == 'GET':
            if self.request.user.is_authenticated:
                return Event.objects.filter(Q(owner=self.request.user) | Q(status='approved')).distinct()
            return Event.objects.filter(status='approved')
        
        # Edit/Delete only for owner
        return Event.objects.filter(owner=self.request.user)

class EventLikeToggleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        
        if event.likes.filter(id=user.id).exists():
            event.likes.remove(user)
            return api_response('success', 'Event removed from favorites', {'is_liked': False})
        else:
            event.likes.add(user)
            return api_response('success', 'Event added to favorites', {'is_liked': True})

# AdminCreatedEventListAPIView moved to bottom of file

# --------------------------
# Admin Event Views
# --------------------------

class AdminEventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/admin/event_list_v2.html'
    context_object_name = 'events'
    paginate_by = 20
    ordering = ['-created_at']
    login_url = 'admin_login'
    
    def get_queryset(self):
        status_filter = self.request.GET.get('status', 'approved') # Default to approved
        queryset = super().get_queryset()
        
        # New Filters
        # 1. Date From
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(event_date__gte=date_from)
            
        # 2. Event Name Search
        event_name = self.request.GET.get('event_name')
        if event_name:
            queryset = queryset.filter(title__icontains=event_name)
            
        # 3. Category Filter
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # 4. Owner Search
        owner_name = self.request.GET.get('owner')
        if owner_name:
            queryset = queryset.filter(
                Q(owner__full_name__icontains=owner_name) | 
                Q(owner__phone_number__icontains=owner_name)
            )

        if status_filter == 'all':
             return queryset
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Pass categories for filter dropdown
        context['categories'] = EventCategory.objects.all()
        
        # Calculate counts
        context['all_count'] = Event.objects.count()
        context['pending_count'] = Event.objects.filter(status='pending').count()
        context['approved_count'] = Event.objects.filter(status='approved').count()
        context['rejected_count'] = Event.objects.filter(status='rejected').count()
        context['blocked_count'] = Event.objects.filter(status='blocked').count()
        context['finished_count'] = Event.objects.filter(status='finished').count()
        
        return context

class AdminEventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'events/admin/event_create.html'
    success_url = '/admin/events/'
    login_url = 'admin_login'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'approved' # Auto-approve admin events
        
        # Set prices to 0 if payment type is free
        if form.instance.payment_type == 'free':
            form.instance.regular_price = 0
            form.instance.offer_price = 0
        
        response = super().form_valid(form)
        
        # Handle Gallery Images
        try:
            gallery_images = self.request.FILES.getlist('gallery_images')
            for image in gallery_images:
                EventGalleryImage.objects.create(event=self.object, image=image)
        except Exception as e:
            # Log the error but don't fail the whole event creation
            print(f"Error uploading gallery images: {e}")
            messages.warning(self.request, f"Event created, but some gallery images failed to upload: {e}")
        
        # Handle Scratch Prizes
        try:
            prize_titles = self.request.POST.getlist('prize_title_[]')
            prize_descriptions = self.request.POST.getlist('prize_description_[]')
            prize_codes = self.request.POST.getlist('prize_code_[]')
            prize_expiries = self.request.POST.getlist('prize_expiry_date_[]')
            prize_is_better_luck = self.request.POST.getlist('prize_is_better_luck_[]')
            prize_images = self.request.FILES.getlist('prize_image_[]')
            
            # Create ScratchPrize objects
            for i, title in enumerate(prize_titles):
                if title.strip():  # Only create if title is not empty
                    is_better_luck = str(i) in prize_is_better_luck or (i < len(prize_is_better_luck) and prize_is_better_luck[i] == '1')
                    
                    expiry_date = None
                    if i < len(prize_expiries) and prize_expiries[i]:
                        try:
                            parsed_date = datetime.datetime.strptime(prize_expiries[i], '%Y-%m-%d').date()
                            if self.object.event_date and parsed_date < self.object.event_date:
                                messages.warning(self.request, f"Expiry date cannot be before event date for '{title}'.")
                            else:
                                expiry_date = parsed_date
                        except ValueError:
                            pass

                    prize = ScratchPrize.objects.create(
                        event=self.object,
                        title=title,
                        description=prize_descriptions[i] if i < len(prize_descriptions) else '',
                        code=prize_codes[i] if i < len(prize_codes) else '',
                        is_better_luck=is_better_luck,
                        expiry_date=expiry_date,
                        total_count=-1  # Unlimited by default
                    )
                    
                    # Handle image if provided
                    if i < len(prize_images):
                        prize.image = prize_images[i]
                        prize.save()
        except Exception as e:
            print(f"Error creating scratch prizes: {e}")
            messages.warning(self.request, f"Event created, but some scratch prizes failed to save: {e}")
            
        # Generate QR for this new event
        generate_event_qr(self.object)
        return response

class AdminEventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'events/admin/event_create.html'
    login_url = 'admin_login'

    def get_success_url(self):
        return reverse_lazy('admin_event_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # Set prices to 0 if payment type is free
        if form.instance.payment_type == 'free':
            form.instance.regular_price = 0
            form.instance.offer_price = 0
        
        response = super().form_valid(form)
        
        # Handle Gallery Images (Append new ones)
        try:
            gallery_images = self.request.FILES.getlist('gallery_images')
            for image in gallery_images:
                EventGalleryImage.objects.create(event=self.object, image=image)
        except Exception as e:
             messages.warning(self.request, f"Event updated, but gallery images failed: {e}")
            
        messages.success(self.request, 'Event updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

class AdminEventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'events/admin/event_detail_v2.html'
    context_object_name = 'event'
    login_url = 'admin_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        total_booked = event.bookings.filter(status__in=['booked', 'attended']).aggregate(Sum('ticket_count'))['ticket_count__sum'] or 0
        context['total_booked_tickets'] = total_booked
        context['edit_history'] = EventEditHistory.objects.filter(event=event).order_by('-changed_at')
        context['edit_history'] = EventEditHistory.objects.filter(event=event).order_by('-changed_at')
        return context

class AdminEventUpdatePaymentStatusView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        status = request.POST.get('admin_payment_status')
        note = request.POST.get('admin_payment_note')
        
        if status in dict(Event.ADMIN_PAYMENT_STATUS_CHOICES):
            event.admin_payment_status = status
            
        if note is not None:
             event.admin_payment_note = note
             
        event.save()
        messages.success(request, f'Payment status updated to {event.get_admin_payment_status_display()}.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventApproveView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        # Capture coins and prizes from the approval form
        coins = request.POST.get('attendee_coins')
        if coins:
            try:
                event.attendee_coins = int(coins)
            except ValueError:
                pass
        
        # Capture scratch prizes (text)
        prizes = request.POST.get('scratch_prizes')
        if prizes:
            event.scratch_prizes = prizes
            
        event.status = 'approved'
        
        # Generate QR Code
        generate_event_qr(event)
        
        event.save()
        
        Notification.objects.create(
            recipient=event.owner,
            title="Event Approved",
            message=f"Your event '{event.title}' has been approved.",
            notification_type="event_approval",
            related_id=event.id
        )
        
        messages.success(request, f'Event "{event.title}" has been approved with updated rewards.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventRejectView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        reason = request.POST.get('rejection_reason', 'No reason provided')
        event.rejection_reason = reason
        event.status = 'rejected'
        event.save()
        
        Notification.objects.create(
            recipient=event.owner,
            title="Event Rejected",
            message=f"Your event '{event.title}' has been rejected. Reason: {reason}",
            notification_type="event_rejection",
            related_id=event.id
        )
        
        messages.success(request, f'Event "{event.title}" has been rejected.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventBlockView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        reason = request.POST.get('block_reason', 'No reason provided')
        event.status = 'blocked'
        event.rejection_reason = reason # Reusing this field for block reason
        event.save()
        messages.success(request, f'Event "{event.title}" has been blocked.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventUnblockView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.status = 'approved'
        event.rejection_reason = None # Clear reason
        event.save()
        messages.success(request, f'Event "{event.title}" has been re-approved/unblocked.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventToggleFeaturedView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.is_featured = not event.is_featured
        event.save()
        status = "featured" if event.is_featured else "un-featured"
        messages.success(request, f'Event "{event.title}" is now {status}.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventFinishView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        finish_reason = request.POST.get('finish_reason', '')
        
        event.status = 'finished'
        if finish_reason:
            event.rejection_reason = finish_reason
            
        event.save()
        messages.success(request, f'Event "{event.title}" has been marked as finished.')
        return redirect('admin_event_detail', pk=pk)

class AdminEventToggleSensitiveEditView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.can_edit_sensitive_data = not event.can_edit_sensitive_data
        event.save()
        status = "enabled" if event.can_edit_sensitive_data else "disabled"
        messages.success(request, f'Sensitive data editing {status} for "{event.title}".')
        return redirect('admin_event_detail', pk=pk)

class AdminEventGalleryImageDeleteView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        image = get_object_or_404(EventGalleryImage, pk=pk)
        event_pk = image.event.pk
        image.delete()
        messages.success(request, 'Gallery image deleted successfully.')
        return redirect('admin_event_detail', pk=event_pk)

class AdminEventUpdateRewardsView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        
        # Capture coins
        coins = request.POST.get('attendee_coins')
        if coins:
            try:
                event.attendee_coins = int(coins)
            except ValueError:
                pass
        
        event.save()
        
        # Handle prize deletions
        prize_deletes = request.POST.getlist('prize_delete_[]')
        for prize_id in prize_deletes:
            try:
                prize = ScratchPrize.objects.get(id=prize_id, event=event)
                prize.delete()
            except ScratchPrize.DoesNotExist:
                pass
        
        # Handle existing prize updates
        prize_ids = request.POST.getlist('prize_id_[]')
        for prize_id in prize_ids:
            try:
                prize = ScratchPrize.objects.get(id=prize_id, event=event)
                
                # Update fields
                title = request.POST.get(f'prize_title_{prize_id}')
                if title:
                    prize.title = title
                
                prize.description = request.POST.get(f'prize_description_{prize_id}', '')
                prize.code = request.POST.get(f'prize_code_{prize_id}', '')
                prize.is_better_luck = request.POST.get(f'prize_is_better_luck_{prize_id}') == '1'
                
                # Handle Expiry Date
                expiry_str = request.POST.get(f'prize_expiry_date_{prize_id}')
                if expiry_str:
                    try:
                        expiry_date = datetime.datetime.strptime(expiry_str, '%Y-%m-%d').date()
                        if event.event_date and expiry_date < event.event_date:
                             messages.warning(request, f"Expiry date cannot be before event date for '{prize.title}'.")
                        else:
                             prize.expiry_date = expiry_date
                    except ValueError:
                        pass
                else:
                    prize.expiry_date = None

                # Handle image update
                image_file = request.FILES.get(f'prize_image_{prize_id}')
                if image_file:
                    prize.image = image_file
                
                prize.save()
            except ScratchPrize.DoesNotExist:
                pass
        
        # Handle new prizes
        new_titles = request.POST.getlist('prize_title_new_[]')
        new_descriptions = request.POST.getlist('prize_description_new_[]')
        new_codes = request.POST.getlist('prize_code_new_[]')
        new_expiries = request.POST.getlist('prize_expiry_date_new_[]')
        new_is_better_luck = request.POST.getlist('prize_is_better_luck_new_[]')
        new_images = request.FILES.getlist('prize_image_new_[]')
        
        for i, title in enumerate(new_titles):
            if title.strip():
                is_better_luck = str(i) in new_is_better_luck or (i < len(new_is_better_luck) and new_is_better_luck[i] == '1')
                
                expiry_date = None
                if i < len(new_expiries) and new_expiries[i]:
                    try:
                        parsed_date = datetime.datetime.strptime(new_expiries[i], '%Y-%m-%d').date()
                        if event.event_date and parsed_date < event.event_date:
                            messages.warning(request, f"Expiry date cannot be before event date for '{title}'.")
                        else:
                            expiry_date = parsed_date
                    except ValueError:
                        pass

                prize = ScratchPrize.objects.create(
                    event=event,
                    title=title,
                    description=new_descriptions[i] if i < len(new_descriptions) else '',
                    code=new_codes[i] if i < len(new_codes) else '',
                    is_better_luck=is_better_luck,
                    expiry_date=expiry_date,
                    total_count=-1
                )
                
                # Handle image if provided
                if i < len(new_images):
                    prize.image = new_images[i]
                    prize.save()
        
        messages.success(request, f'Rewards updated for "{event.title}".')
        return redirect('admin_event_detail', pk=pk)

# --------------------------
# Host Request API Views
# --------------------------

class HostRequestCreateAPIView(generics.CreateAPIView):
    queryset = HostRequest.objects.all()
    serializer_class = HostRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure user doesn't have a pending request already?
        # For now, just create.
        serializer.save(user=self.request.user)

# --------------------------
# User Features API
# --------------------------

class BookingCreateAPIView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        event = serializer.validated_data['event']
        ticket_count = serializer.validated_data['ticket_count']
        
        # Check Capacity
        if event.maximum_capacity > 0:
            booked = event.bookings.filter(status__in=['booked', 'attended']).aggregate(total=Sum('ticket_count'))['total'] or 0
            ten_minutes_ago = timezone.now() - datetime.timedelta(minutes=10)
            pending = event.bookings.filter(status='pending_payment', booking_date__gte=ten_minutes_ago).aggregate(total=Sum('ticket_count'))['total'] or 0
            current_bookings = booked + pending
            if current_bookings + ticket_count > event.maximum_capacity:
                 raise serializers.ValidationError(f"Booking exceeds maximum capacity. Only {event.maximum_capacity - current_bookings} seats left.")

        # Calculate total price
        price = event.offer_price if event.offer_price and event.offer_price > 0 else event.regular_price
        total = price * ticket_count
        
        booking = serializer.save(user=self.request.user, total_price=total)
        
        Notification.objects.create(
            recipient=event.owner,
            title="New Booking",
            message=f"A new booking of {ticket_count} ticket(s) has been made for '{event.title}' by {self.request.user.full_name}.",
            notification_type="new_booking",
            related_id=event.id
        )

class CreateRazorpayOrderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        event_id = request.data.get('event_id')
        ticket_count = int(request.data.get('ticket_count', 1))

        # Guest Info
        guest_name = request.data.get('guest_name')
        guest_email = request.data.get('guest_email')
        guest_phone_number = request.data.get('guest_phone_number')
        guest_country_code = request.data.get('guest_country_code')
        
        if not event_id:
            return api_response('error', 'Event ID is required', status_code=400)

        event = get_object_or_404(Event, pk=event_id)
        
        # Check Capacity
        if event.maximum_capacity > 0:
            booked = event.bookings.filter(status__in=['booked', 'attended']).aggregate(total=Sum('ticket_count'))['total'] or 0
            ten_minutes_ago = timezone.now() - datetime.timedelta(minutes=10)
            pending = event.bookings.filter(status='pending_payment', booking_date__gte=ten_minutes_ago).aggregate(total=Sum('ticket_count'))['total'] or 0
            current_bookings = booked + pending
            if current_bookings + ticket_count > event.maximum_capacity:
                 return api_response('error', f'Only {event.maximum_capacity - current_bookings} tickets left.', status_code=400)
        
        # Calculate amount in paise
        # Use offer_price if available and > 0, else regular_price
        price = event.offer_price if event.offer_price > 0 else event.regular_price
        total_amount = price * ticket_count
        
        amount_paise = int(total_amount * 100) 
        currency = "INR"
        
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
             return api_response('error', 'Razorpay keys not configured', status_code=500)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        receipt = f"rcpt_{request.user.id}_{int(timezone.now().timestamp())}"
        
        data = { 
            "amount": amount_paise, 
            "currency": currency, 
            "receipt": receipt, 
            "notes": { 
                "event_id": event_id,
                "ticket_count": ticket_count,
                 "user_id": request.user.id,
                 "guest_name": guest_name,
                 "guest_email": guest_email,
                 "guest_phone": guest_phone_number
            } 
        }
        try:
            order = client.order.create(data=data)
            
            # Create a pending payment booking to hold the capacity
            Booking.objects.create(
                user=request.user,
                event=event,
                ticket_count=ticket_count,
                total_price=total_amount,
                transaction_id=order['id'],
                status='pending_payment',
                guest_name=guest_name,
                guest_email=guest_email,
                guest_phone_number=guest_phone_number,
                guest_country_code=guest_country_code
            )
            
            # Add Key ID to response for frontend convenience
            order['key_id'] = settings.RAZORPAY_KEY_ID
            order['event_title'] = event.title
            
            return api_response('success', 'Order Created', order)
        except Exception as e:
            return api_response('error', str(e), status_code=500)
        except Exception as e:
            return api_response('error', str(e), status_code=500)

class VerifyRazorpayPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return api_response('error', 'Missing payment parameters', status_code=400)
            
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            # Fetch order details to know the event and user
            order = client.order.fetch(razorpay_order_id)
            notes = order.get('notes', {})
            event_id = notes.get('event_id')
            ticket_count = int(notes.get('ticket_count', 1))
            
            if not event_id:
                return api_response('error', 'Invalid order notes', status_code=400)
                
            booking = Booking.objects.filter(transaction_id=razorpay_order_id).first()
            if not booking:
                event = get_object_or_404(Event, pk=event_id)
                price = event.offer_price if event.offer_price > 0 else event.regular_price
                total = price * ticket_count
                
                booking = Booking.objects.create(
                    user=request.user,
                    event=event,
                    ticket_count=ticket_count,
                    total_price=total,
                    transaction_id=razorpay_order_id,
                    status='pending_payment'
                )
                
            if booking.status == 'pending_payment':
                booking.payment_id = razorpay_payment_id
                booking.payment_status = 'completed'
                booking.payment_source = 'api'
                booking.paid_amount = order.get('amount_paid', 0) / 100
                booking.paid_at = timezone.now()
                booking.status = 'booked'
                booking.save()
                
                Notification.objects.create(
                    recipient=booking.event.owner,
                    title="New Booking (Razorpay)",
                    message=f"A new booking of {booking.ticket_count} ticket(s) has been made for '{booking.event.title}' by {request.user.full_name}.",
                    notification_type="new_booking",
                    related_id=booking.event.id
                )
            
            return api_response('success', 'Payment verified and booking successful', {
                'booking_id': booking.id,
                'booking_code': booking.booking_code
            })
            
        except razorpay.errors.SignatureVerificationError:
            return api_response('error', 'Invalid payment signature', status_code=400)
        except Exception as e:
            return api_response('error', f'Payment verification failed: {str(e)}', status_code=500)

class RazorpayWebhookAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', getattr(settings, 'RAZORPAY_KEY_SECRET', ''))
        
        if not webhook_signature:
            return Response({'status': 'missing signature'}, status=400)

        payload = request.body.decode('utf-8')
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            client.utility.verify_webhook_signature(payload, webhook_signature, webhook_secret)
        except razorpay.errors.SignatureVerificationError:
            return Response({'status': 'invalid signature'}, status=400)
            
        data = request.data
        event_type = data.get('event')
        
        if event_type == 'order.paid':
            payload_order = data.get('payload', {}).get('order', {}).get('entity', {})
            payload_payment = data.get('payload', {}).get('payment', {}).get('entity', {})
            
            order_id = payload_order.get('id')
            payment_id = payload_payment.get('id')
            notes = payload_order.get('notes', {})
            
            event_id = notes.get('event_id')
            ticket_count = int(notes.get('ticket_count', 1))
            user_id = notes.get('user_id')
            
            if event_id and user_id and order_id:
                # Check if booking exists
                booking = Booking.objects.filter(transaction_id=order_id).first()
                if not booking:
                    event = Event.objects.filter(pk=event_id).first()
                    user = User.objects.filter(pk=user_id).first()
                    
                    if event and user:
                        price = event.offer_price if event.offer_price > 0 else event.regular_price
                        total = price * ticket_count
                        
                        booking = Booking.objects.create(
                            user=user,
                            event=event,
                            ticket_count=ticket_count,
                            total_price=total,
                            transaction_id=order_id,
                            status='pending_payment'
                        )
                
                if booking and booking.status == 'pending_payment':
                    booking.payment_id = payment_id
                    booking.payment_status = 'completed'
                    booking.payment_source = 'webhook'
                    booking.paid_amount = payload_order.get('amount_paid', 0) / 100
                    booking.paid_at = timezone.now()
                    booking.status = 'booked'
                    booking.save()
                    
                    Notification.objects.create(
                        recipient=booking.event.owner,
                        title="New Booking (Webhook)",
                        message=f"A new booking of {booking.ticket_count} ticket(s) has been made for '{booking.event.title}' by {booking.user.full_name}.",
                        notification_type="new_booking",
                        related_id=booking.event.id
                    )

        return Response({'status': 'ok'})

class RazorpayKeysAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if hasattr(settings, 'RAZORPAY_KEY_ID') and settings.RAZORPAY_KEY_ID:
            return api_response('success', 'Razorpay Keys', {
                'key_id': settings.RAZORPAY_KEY_ID,
                'key_secret': getattr(settings, 'RAZORPAY_KEY_SECRET', None)
            })
        return api_response('error', 'Razorpay keys not configured on server', status_code=500)

class BookingListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        bookings = Booking.objects.filter(user=request.user, status__in=['booked', 'attended']).order_by('-booking_date')

        upcoming = bookings.filter(event__event_date__gte=today)
        completed = bookings.filter(event__event_date__lt=today)

        upcoming_data = BookingSerializer(upcoming, many=True, context={'request': request}).data
        completed_data = BookingSerializer(completed, many=True, context={'request': request}).data

        return api_response('success', 'Bookings fetched', {
            'upcoming': upcoming_data,
            'completed': completed_data
        })

class HostEventBookingListAPIView(generics.ListAPIView):
    serializer_class = HostBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Allow staff to see all, otherwise only owner events
        if self.request.user.is_staff:
             queryset = Booking.objects.filter(status__in=['booked', 'attended']).order_by('-booking_date')
        else:
             queryset = Booking.objects.filter(event__owner=self.request.user, status__in=['booked', 'attended']).order_by('-booking_date')
        
        event_id = self.request.query_params.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        # Search Filter (User Name, Email, Phone)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search) |
                Q(booking_code__icontains=search)
            )
            
        # Date Range Filter
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(booking_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(booking_date__date__lte=date_to)
            
        if date_to:
            queryset = queryset.filter(booking_date__date__lte=date_to)
            
        return queryset

    def list(self, request, *args, **kwargs):
        # Validate ownership if event_id is provided
        event_id = request.query_params.get('event_id')
        if event_id:
             try:
                 event = Event.objects.get(pk=event_id)
                 if event.owner != request.user and not request.user.is_staff:
                     return api_response('error', 'You are not the owner of this event or authorized to view its bookings', status_code=403)
             except Event.DoesNotExist:
                 return api_response('error', 'Event not found', status_code=404)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Calculate stats on full queryset (ignoring pagination)
            total_booked_tickets = queryset.aggregate(Sum('ticket_count'))['ticket_count__sum'] or 0
            total_amount_collected = queryset.aggregate(Sum('total_price'))['total_price__sum'] or 0
            
            # Calculate Available Tickets (Pending Count) - Global for the context
            available_balance = 0
            if event_id:
                 # event object is available from the validated fetch at logic start
                 if event.maximum_capacity > 0:
                     sold_count = Booking.objects.filter(event=event).exclude(status='cancelled').aggregate(Sum('ticket_count'))['ticket_count__sum'] or 0
                     available_balance = max(0, event.maximum_capacity - sold_count)
            else:
                 # Aggregate finite capacity events for the host
                 finite_events = Event.objects.filter(owner=request.user, maximum_capacity__gt=0)
                 if finite_events.exists():
                     total_cap = finite_events.aggregate(Sum('maximum_capacity'))['maximum_capacity__sum'] or 0
                     total_sold = Booking.objects.filter(event__in=finite_events).exclude(status='cancelled').aggregate(Sum('ticket_count'))['ticket_count__sum'] or 0
                     available_balance = max(0, total_cap - total_sold)
            
            response.data['total_booked_tickets'] = total_booked_tickets
            response.data['total_amount_collected'] = total_amount_collected
            response.data['available_balance'] = available_balance
            
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class EventBookingExportAPIView(APIView):
    permission_classes = [permissions.AllowAny] # Changed to AllowAny to handle manual token check

    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
             return api_response('error', 'Event not found', status_code=404)
        
        # No authorization check needed as requested
        pass
             
        bookings = Booking.objects.filter(event=event).order_by('-booking_date')
        
        response = HttpResponse(content_type='text/csv')
        filename = f"bookings_{event.id}_{event.title[:10].replace(' ', '_')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Booking ID', 'Booking Code', 'Event', 'User', 'Booking User Email', 'Booking User Mobile', 'Tickets', 'Total Price', 'Status', 'Date'])
        
        for booking in bookings:
            writer.writerow([
                booking.id,
                booking.booking_code or '-',
                booking.event.title,
                booking.user.full_name or booking.user.phone_number,
                booking.user.email,
                booking.user.phone_number,
                booking.ticket_count,
                booking.total_price,
                booking.get_status_display(),
                booking.booking_date.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response

class AttendEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        qr_token = request.data.get('qr_token')
        if not qr_token:
            return api_response('error', 'QR Token is required', status_code=400)
        
        try:
            event = Event.objects.get(qr_code_token=qr_token)
        except Event.DoesNotExist:
            return api_response('error', 'Invalid QR Code', status_code=404)
            
        # Date Validation
        today = timezone.now().date()
        if event.event_date and event.event_date != today:
            if today < event.event_date:
                return api_response('error', f'Event has not started yet. Please check in on {event.event_date}.', status_code=400)
            else:
                return api_response('error', f'This event has expired. Event date was {event.event_date}.', status_code=400)
        
        user = request.user
        
        # Check if user has a booking
        booking = Booking.objects.filter(user=user, event=event, status='booked').first()
        if not booking:
            # Check if they already attended
            if Booking.objects.filter(user=user, event=event, status='attended').exists():
                 return api_response('error', 'You have already checked in for this event.', status_code=400)
            return api_response('error', 'No valid booking found for this event.', status_code=400)
        
        # Process Attendance (Atomic transaction)
        with transaction.atomic():
            # 1. Update Booking
            booking.status = 'attended'
            booking.save()
            
            # 2. Credit Coins
            if event.attendee_coins > 0:
                user.wallet_balance += event.attendee_coins
                user.save()
                WalletTransaction.objects.create(
                    user=user, 
                    amount=event.attendee_coins, 
                    description=f"Reward for attending {event.title}"
                )
            
            # 3. Generate Scratch Card
            # Use ScratchPrize items
            available_prizes = event.scratch_prize_items.filter(
                Q(total_count=-1) | Q(won_count__lt=F('total_count'))
            )
            
            selected_prize = "Better Luck Next Time"
            prize_obj = None

            if available_prizes.exists():
                prize_obj = random.choice(list(available_prizes))
                selected_prize = prize_obj.title
                prize_obj.won_count += 1
                prize_obj.save()
            
            scratch_card = ScratchCard.objects.create(
                user=user,
                event=event,
                prize_text=selected_prize,
                prize=prize_obj
            )
            
        # Prepare prize details for response
        prize_details = {
            'prize_text': selected_prize,
            'prize_image': prize_obj.image.url if prize_obj and prize_obj.image else None,
            'prize_description': prize_obj.description if prize_obj else None,
            'prize_code': prize_obj.code if prize_obj else None,
            'expiry_date': prize_obj.expiry_date.strftime('%Y-%m-%d') if prize_obj and prize_obj.expiry_date else None,
            'is_better_luck': prize_obj.is_better_luck if prize_obj else True
        }
        
        return api_response('success', 'Checked in successfully! You got coins and a scratch card.', data={
            'coins_earned': event.attendee_coins,
            'scratch_card_id': scratch_card.id,
            'prize': prize_details
        })

class ScratchCardListAPIView(generics.ListAPIView):
    serializer_class = ScratchCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ScratchCard.objects.filter(user=self.request.user).order_by('-created_at')

class ScratchCardRevealAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(ScratchCard, pk=pk, user=request.user)
        
        # Prepare Response Details
        prize_details = {
             'prize': card.prize_text,
             'is_better_luck': False,
             'image': None,
             'description': '',
             'code': ''
        }
        
        # Enrich from config
        prize_config = ScratchPrize.objects.filter(event=card.event, title=card.prize_text).first()
        if prize_config:
             prize_details['is_better_luck'] = prize_config.is_better_luck
             prize_details['description'] = prize_config.description or ''
             prize_details['code'] = prize_config.code or ''
             if prize_config.image:
                 prize_details['image'] = request.build_absolute_uri(prize_config.image.url)

        if card.is_scratched:
            return api_response('success', 'Card is already scratched', prize_details)
            
        card.is_scratched = True
        card.save()
        
        return api_response('success', 'Card scratched!', prize_details)

class WalletHistoryAPIView(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        total_balance = request.user.wallet_balance
        total_balance = request.user.wallet_balance
        # Calculate Scratch Card Count for 'total_price_count' per user request
        total_price_count = ScratchCard.objects.filter(user=request.user).count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['total_balance'] = total_balance
            response.data['total_balance'] = total_balance
            response.data['total_price_count'] = total_price_count # This is now the count of scratch cards
            return response
            return response

        serializer = self.get_serializer(queryset, many=True)
        return api_response('success', 'Wallet history', {
            'transactions': serializer.data,
            'total_balance': total_balance,
            'total_price_count': total_price_count
        })

# --------------------------
# Social Features API
# --------------------------

class LikeEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        
        if not event.likes.filter(id=user.id).exists():
            event.likes.add(user)
            
        return api_response('success', 'Event liked', {'is_liked': True})

class UnlikeEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        
        if event.likes.filter(id=user.id).exists():
            event.likes.remove(user)
            
        return api_response('success', 'Event unliked', {'is_liked': False})

class ToggleFavoriteEventAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user
        
        if event.favorites.filter(id=user.id).exists():
            event.favorites.remove(user)
            return api_response('success', 'Event unfavorited', {'is_favorited': False})
        else:
            event.favorites.add(user)
            return api_response('success', 'Event favorited', {'is_favorited': True})

class ToggleFollowUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        
        if target_user == request.user:
             return api_response('error', 'You cannot follow yourself', status_code=400)
             
        if request.user.following.filter(id=target_user.id).exists():
            request.user.following.remove(target_user)
            return api_response('success', f'Unfollowed {target_user.full_name}')
        else:
            request.user.following.add(target_user)
            Notification.objects.create(
                recipient=target_user,
                title="New Follower",
                message=f"{request.user.full_name} started following you.",
                notification_type="new_follower",
                related_id=request.user.id
            )
            return api_response('success', f'Followed {target_user.full_name}')

class ToggleLikeProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        
        if target_user == request.user:
             return api_response('error', 'You cannot like yourself', status_code=400)
             
        # Check if request.user has liked target_user
        if request.user.profile_likes.filter(id=target_user.id).exists():
            request.user.profile_likes.remove(target_user)
            return api_response('success', f'Unliked {target_user.full_name}')
        else:
            request.user.profile_likes.add(target_user)
            return api_response('success', f'Liked {target_user.full_name}')

class HostListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = User.objects.exclude(user_type='regular').filter(is_active=True).exclude(host_name__isnull=True).exclude(host_name__exact='').order_by('-date_joined')
        
        # Filter by multiple user types
        user_types = self.request.GET.getlist('user_type')
        if not user_types:
             ut_param = self.request.GET.get('user_type')
             if ut_param:
                 user_types = ut_param.split(',')
        
        if user_types:
            queryset = queryset.filter(user_type__in=user_types)
            
        # Filter by multiple category types
        category_ids = self.request.GET.getlist('category_id') # e.g. ?category_id=1&category_id=2
        if not category_ids:
             # Check for comma separated string
             cat_param = self.request.GET.get('category_id')
             if cat_param:
                 category_ids = cat_param.split(',')

        if category_ids:
            queryset = queryset.filter(host_category__id__in=category_ids)
            
        # Search (Host Name or Category Name)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(host_name__icontains=search) |
                Q(host_category__name__icontains=search)
            )
            
        return queryset

class LikedEventsListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        user = self.request.user
        queryset = user.liked_events.all().order_by('-created_at')

        # Category Filter
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Type Filter (Event, Experience, etc.)
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(owner__user_type=type_param)

        return queryset

class FavoritedEventsListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        user = self.request.user
        queryset = user.favorited_events.all().order_by('-created_at')

        # Category Filter
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Type Filter (Event, Experience, etc.)
        type_param = self.request.query_params.get('type')
        if type_param:
            queryset = queryset.filter(owner__user_type=type_param)

        return queryset

class LikedProfilesListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'host_name', 'email', 'phone_number']

    def get_queryset(self):
        user = self.request.user
        queryset = user.profile_likes.all().order_by('full_name')

        # User Type Filter (artist, venue_owner, experience_provider)
        user_type = self.request.query_params.get('type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        return queryset

class FollowingListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'host_name', 'email', 'phone_number']

    def get_queryset(self):
        user = self.request.user
        queryset = user.following.all().order_by('full_name')

        # User Type Filter
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        return queryset

class FollowersListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'host_name', 'email', 'phone_number']

    def get_queryset(self):
        user = self.request.user
        queryset = user.followers.all().order_by('full_name')

        # User Type Filter
        user_type = self.request.query_params.get('user_type')
        if user_type:
            queryset = queryset.filter(user_type=user_type)

        return queryset

class HostDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserHostDetailSerializer
    permission_classes = [permissions.AllowAny]

class HostGalleryManageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        images = HostGalleryImage.objects.filter(user=request.user).order_by('-created_at')
        return api_response('success', 'Gallery images loaded', HostGalleryImageSerializer(images, many=True).data)

    def post(self, request):
        # Handle multiple file uploads
        files = request.FILES.getlist('images')
        if not files:
             return api_response('error', 'No images provided', status_code=400)
        
        created_images = []
        for file in files:
            image = HostGalleryImage.objects.create(user=request.user, image=file)
            created_images.append(image)
        
        return api_response('success', 'Images uploaded successfully', HostGalleryImageSerializer(created_images, many=True).data)

    def delete(self, request):
        image_ids = request.data.get('image_ids', [])
        if not image_ids:
             return api_response('error', 'No image IDs provided', status_code=400)
             
        HostGalleryImage.objects.filter(user=request.user, id__in=image_ids).delete()
        return api_response('success', 'Images deleted successfully')

class ActiveEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny] # Allow public to see active events? Or IsAuthenticated
    
    def get_queryset(self):
        today = timezone.now().date()
        queryset = Event.objects.filter(status='approved', event_date__gte=today).order_by('-start_time')
        
        # Filter by Category
        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by User Type (of the owner)
        owner_type = self.request.GET.get('owner_type')
        if owner_type:
            queryset = queryset.filter(owner__user_type=owner_type)
            
        # Date Filter
        date_param = self.request.GET.get('date')
        if date_param:
            try:
                queryset = queryset.filter(event_date=date_param)
            except ValueError:
                pass

        # Month Filter
        month_param_raw = self.request.GET.get('month')
        year_param = self.request.GET.get('year')
        if month_param_raw:
            try:
                if '-' in month_param_raw:
                    y, m = month_param_raw.split('-')
                    queryset = queryset.filter(event_date__year=int(y), event_date__month=int(m))
                else:
                    m = int(month_param_raw)
                    y = int(year_param) if year_param else timezone.now().year
                    queryset = queryset.filter(event_date__year=y, event_date__month=m)
            except ValueError:
                pass
            
        return queryset

# --------------------------
# General / User API Views
# --------------------------

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token") or request.data.get("refresh")
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except AttributeError:
                    # Blacklist app might not be installed
                    pass
                except Exception as e:
                    print(f"Refresh Blacklist error: {e}")
                    
            # Explicitly Blacklist Access Token
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token_str = auth_header.split(' ')[1]
                from rest_framework_simplejwt.tokens import AccessToken
                from django.core.cache import cache
                import time
                try:
                    access_token = AccessToken(access_token_str)
                    jti = access_token.get('jti')
                    exp_time = access_token.get('exp')
                    timeout = exp_time - int(time.time())
                    if timeout > 0:
                        cache.set(f"blacklisted_token_{jti}", True, timeout=timeout)
                except Exception as e:
                    print(f"Access token blacklist error: {e}")

            return api_response('success', 'Logged out successfully')
        except Exception as e:
            print(f"Logout error: {str(e)}")
            # Even if token is already expired/invalid, standard behavior for logout is success
            return api_response('success', 'Logged out locally (token invalid or already expired)')

class AppFeedbackCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .serializers import AppFeedbackSerializer
        serializer = AppFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return api_response('success', 'Feedback submitted successfully')
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class ChangePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
             return api_response('error', 'Both old and new passwords are required', status_code=400)
             
        if not user.check_password(old_password):
            return api_response('error', 'Invalid old password', status_code=400)
            
        user.set_password(new_password)
        user.save()
        
        return api_response('success', 'Password changed successfully')

class SoftDeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        # Mark as deleted
        user.is_active = False
        if user.phone_number:
            # Add _00 to phone number, making sure we don't exceed the 15-character limit
            user.phone_number = user.phone_number[:12] + "_00"
        if user.email:
            # Add _00 to email
            user.email = user.email + "_00"
        user.save()
        
        # Blacklist current token if possible
        try:
            refresh_token = request.data.get("refresh_token") or request.data.get("refresh")
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
            
        return api_response('success', 'Account deleted successfully', status_code=200)

class UserEventActionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        action = request.data.get('action') # activate, block, delete
        try:
            event = Event.objects.get(pk=pk, owner=request.user)
        except Event.DoesNotExist:
             return api_response('error', 'Event not found or permission denied', status_code=404)

        if action == 'delete':
            event.delete()
            return api_response('success', 'Event deleted successfully')
        
        elif action == 'block':
            # User "blocks" their own event -> maybe "cancelled" or "inactive"
            # Using 'blocked' status might be confused with Admin block. 
            # Let's assume they want to "Withdraw" or "Cancel".
            # If the user specifically said "block", I'll use a status for that or local logic.
            # Reuse 'rejected' or add a new status 'cancelled'? 
            # For now, let's toggle a boolean or use 'blocked' if the system allows users to block own.
            # But the model has 'blocked' in choices.
            event.status = 'blocked' 
            event.save()
            return api_response('success', 'Event blocked/cancelled successfully')
            
        elif action == 'activate':
            # "Activate" -> Submit for approval if draft? Or re-enable?
            # If model status is 'blocked', set to 'pending' (re-submit).
            if event.status == 'blocked':
                event.status = 'pending'
                event.save()
                return api_response('success', 'Event activated and submitted for approval')
            elif event.status == 'pending':
                 return api_response('info', 'Event is already pending approval')
            elif event.status == 'approved':
                 return api_response('info', 'Event is already active/approved')
        
        else:
             return api_response('error', 'Invalid action. Use delete, block, or activate', status_code=400)
        
        return api_response('error', 'Action failed', status_code=400)


class HostCategoryListByTypeAPIView(generics.ListAPIView):
    serializer_class = HostCategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = HostCategory.objects.filter(status='active')
        user_type = self.request.query_params.get('user_type')
        
        if user_type:
             queryset = queryset.filter(
                Q(allowed_user_type=user_type) | 
                Q(allowed_user_type__isnull=True) | 
                Q(allowed_user_type='')
             )
        return queryset

class HomeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        today = timezone.now().date()
        
        # 1. (Categories removed)

        # 2. Featured Events (Approved, Featured, Not Expired)
        featured = Event.objects.filter(
            status='approved', 
            is_featured=True, 
            event_date__gte=today
        ).order_by('event_date')
        
        featured_data = EventSerializer(featured, many=True, context={'request': request}).data

        # 3. Upcoming Events
        upcoming = Event.objects.filter(status='approved', event_date__gte=today).order_by('event_date')[:10]
        upcoming_data = EventSerializer(upcoming, many=True, context={'request': request}).data
        
        # 3.1 Recently Past Events (Limit 5)
        recent_past = Event.objects.filter(status='approved', event_date__lt=today).order_by('-event_date')[:5]
        recent_past_data = EventSerializer(recent_past, many=True, context={'request': request}).data
        
        # 4. Limit 5 lists for Artists, Venues, Experients
        artists = User.objects.filter(user_type='artist', is_active=True).exclude(host_name__isnull=True).exclude(host_name__exact='').order_by('?')[:5]
        venues = User.objects.filter(user_type='venue_owner', is_active=True).exclude(host_name__isnull=True).exclude(host_name__exact='').order_by('?')[:5]
        experients = User.objects.filter(user_type='experience_provider', is_active=True).exclude(host_name__isnull=True).exclude(host_name__exact='').order_by('?')[:5]
        
        return api_response('success', 'Home data loaded', {
            # 'categories': categories_data,
            'featured_events': featured_data,
            'upcoming_events': upcoming_data,
            'recently_past_events': recent_past_data,
            'artists': UserSerializer(artists, many=True, context={'request': request}).data,
            'venues': UserSerializer(venues, many=True, context={'request': request}).data,
            'experients': UserSerializer(experients, many=True, context={'request': request}).data,
        })

class GlobalSearchAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
             return api_response('success', 'No query provided', {'events': [], 'hosts': []})
        
        # Search Events
        today = timezone.now().date()
        events = Event.objects.filter(
            Q(title__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query),
            status='approved',
            event_date__gte=today
        )[:10]
        events_data = EventSerializer(events, many=True, context={'request': request}).data
        
        # Search Hosts
        hosts = User.objects.exclude(user_type='regular').filter(
            Q(full_name__icontains=query) | Q(email__icontains=query),
            is_active=True
        ).exclude(host_name__isnull=True).exclude(host_name__exact='')
        
        artists = hosts.filter(user_type='artist')[:10]
        venues = hosts.filter(user_type='venue_owner')[:10]
        experiences = hosts.filter(user_type='experience_provider')[:10]

        artists_data = UserSerializer(artists, many=True, context={'request': request}).data
        venues_data = UserSerializer(venues, many=True, context={'request': request}).data
        experiences_data = UserSerializer(experiences, many=True, context={'request': request}).data
        
        return api_response('success', 'Search results', {
            'events': events_data,
            'artists': artists_data,
            'venues': venues_data,
            'experiences': experiences_data
        })

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add User Stats
        # 1. Total Added Events (Exclude Rejected)
        total_events = Event.objects.filter(owner=instance).exclude(status='rejected').count()
        
        # 2. Total Bookings Count (On their events, status booked/attended)
        total_bookings = Booking.objects.filter(
            event__owner=instance, 
            status__in=['booked', 'attended']
        ).count()
        
        # 3. Total Booking Amount (On their events)
        total_amount = Booking.objects.filter(
            event__owner=instance, 
            status__in=['booked', 'attended']
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        data['total_events_count'] = total_events
        data['total_bookings_count'] = total_bookings
        data['total_booking_amount'] = total_amount
        
        return api_response('success', 'Profile data loaded', data)

# --------------------------
# Admin Host Request Views
# --------------------------

class AdminHostRequestListView(LoginRequiredMixin, ListView):
    model = HostRequest
    template_name = 'events/admin/host_request_list.html'
    context_object_name = 'host_requests'
    paginate_by = 20
    ordering = ['-created_at']
    login_url = 'admin_login'

    def get_queryset(self):
        status_filter = self.request.GET.get('status', '')
        queryset = super().get_queryset()
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

class AdminHostRequestDetailView(LoginRequiredMixin, DetailView):
    model = HostRequest
    template_name = 'events/admin/host_request_detail.html'
    context_object_name = 'host_request'
    login_url = 'admin_login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter HostCategory by the requested_type
        # If requested_type is undefined or something else, maybe show all?
        # But safest is filtering.
        # Assuming allowed_user_type on HostCategory matches keys in User.USER_TYPES
        context['host_categories'] = HostCategory.objects.filter(
            models.Q(allowed_user_type=self.object.requested_type) | 
            models.Q(allowed_user_type__isnull=True) | 
            models.Q(allowed_user_type='')
        ).filter(status='active')
        return context

class AdminHostRequestApproveView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        host_req = get_object_or_404(HostRequest, pk=pk)
        
        if host_req.status != 'pending':
             messages.error(request, 'Request has already been processed.')
             return redirect('admin_host_request_detail', pk=pk)

        # Get Host Category from POST
        host_category_id = request.POST.get('host_category')
        if not host_category_id:
            messages.error(request, 'Please select a host category.')
            return redirect('admin_host_request_detail', pk=pk)
            
        try:
            host_category = HostCategory.objects.get(pk=host_category_id)
        except HostCategory.DoesNotExist:
            messages.error(request, 'Invalid host category selected.')
            return redirect('admin_host_request_detail', pk=pk)

        # Update Request Status
        host_req.status = 'approved'
        host_req.save()
        
        # Update User Type and Category
        user = host_req.user
        user.user_type = host_req.requested_type
        user.host_category = host_category
        user.save()
        
        # Send Notification to the user
        Notification.objects.create(
            recipient=user,
            title="Host Request Approved! 🎉",
            message=f"Congratulations! Your host request has been approved. You are now registered as a {user.get_user_type_display()} under the category '{host_category.name}'. You can now start creating and publishing events on Pluuto.",
            notification_type="host_verified",
        )
        
        messages.success(request, f'Request approved. User upgraded to {user.get_user_type_display()} in category {host_category.name}.')
        return redirect('admin_host_request_list')

class AdminHostRequestRejectView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def post(self, request, pk):
        host_req = get_object_or_404(HostRequest, pk=pk)
        
        if host_req.status != 'pending':
             messages.error(request, 'Request has already been processed.')
             return redirect('admin_host_request_detail', pk=pk)

        reason = request.POST.get('rejection_reason', 'No reason provided')
        
        host_req.status = 'rejected'
        host_req.rejection_reason = reason
        host_req.save()
        
        # Send Notification to the user
        Notification.objects.create(
            recipient=host_req.user,
            title="Host Request Update",
            message=f"Your host request has been reviewed. Unfortunately, it was not approved at this time. Reason: {reason}",
            notification_type="host_verified",
        )
        
        messages.success(request, f'Request rejected.')
        return redirect('admin_host_request_detail', pk=pk)

# --------------------------
# Admin Booking Views
# --------------------------

class AdminBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'events/admin/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 20
    ordering = ['-booking_date']
    login_url = 'admin_login'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Event Filter
        event_id = self.request.GET.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        # Search Filter (User)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search) |
                Q(booking_code__icontains=search)
            )
            
        # Status Filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Date Range Filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(booking_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(booking_date__date__lte=date_to)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass events for filter dropdown
        context['events'] = Event.objects.all()
        try:
            context['selected_event_id'] = int(self.request.GET.get('event_id'))
        except (TypeError, ValueError):
            context['selected_event_id'] = None
        return context

class AdminBookingExportView(LoginRequiredMixin, View):
    login_url = 'admin_login'

    def get(self, request):
        # Replicate Filter Logic
        queryset = Booking.objects.all().order_by('-booking_date')
        
        event_id = request.GET.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search) | 
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search) |
                Q(booking_code__icontains=search)
            )
            
        status = request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(booking_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(booking_date__date__lte=date_to)
            
        # Create CSV Response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Booking ID', 'Booking Code', 'Event', 'User Name', 'User Email', 'User Mobile', 'Tickets', 'Total Price', 'Paid Amount', 'Paid At', 'Status', 'Booking Date'])
        
        for booking in queryset:
            writer.writerow([
                booking.id,
                booking.booking_code or '-',
                booking.event.title,
                booking.user.full_name,
                booking.user.email,
                booking.user.phone_number,
                booking.ticket_count,
                booking.total_price,
                booking.paid_amount,
                booking.paid_at.strftime('%Y-%m-%d %H:%M') if booking.paid_at else '',
                booking.get_status_display(),
                booking.booking_date.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response

class AdminScanResultListView(LoginRequiredMixin, ListView):
    model = ScratchCard
    template_name = 'events/admin/scan_result_list.html'
    context_object_name = 'scan_results'
    paginate_by = 20
    ordering = ['-created_at']
    login_url = 'admin_login'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Event Filter
        event_id = self.request.GET.get('event_id')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        # Search Filter (User)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search) | 
                Q(user__email__icontains=search)
            )
            
        # Scratched Status
        status = self.request.GET.get('status') # scratched, unscratched
        if status == 'scratched':
            queryset = queryset.filter(is_scratched=True)
        elif status == 'unscratched':
            queryset = queryset.filter(is_scratched=False)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.all()
        try:
            context['selected_event_id'] = int(self.request.GET.get('event_id'))
        except (TypeError, ValueError):
            context['selected_event_id'] = None
        return context

class AdminAppFeedbackListView(LoginRequiredMixin, ListView):
    model = AppFeedback
    template_name = 'events/admin/app_feedback_list.html'
    context_object_name = 'feedbacks'
    paginate_by = 20
    ordering = ['-created_at']
    login_url = 'admin_login'

class SendCollaborationRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        event_id = request.data.get('event_id')
        user_ids = request.data.get('user_ids', [])

        event = get_object_or_404(Event, id=event_id)
        if event.owner != request.user:
            return api_response('error', 'You are not the owner of this event', status_code=403)
        
        created_count = 0
        for uid in user_ids:
            try:
                to_user = User.objects.get(id=uid)
                if not CollaborationRequest.objects.filter(event=event, to_user=to_user).exists():
                     CollaborationRequest.objects.create(event=event, from_user=request.user, to_user=to_user)
                     Notification.objects.create(
                         recipient=to_user,
                         title="New Collaboration Request",
                         message=f"{request.user.full_name} has invited you to collaborate on '{event.title}'.",
                         notification_type="collaboration_request",
                         related_id=event.id
                     )
                     created_count += 1
            except User.DoesNotExist:
                continue
        
        return api_response('success', f'Sent collaboration requests to {created_count} users.')

class CollaborationRequestActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        collab_req = get_object_or_404(CollaborationRequest, pk=pk)
        action = request.data.get('action')

        if action == 'accept':
            if collab_req.to_user != request.user:
                return api_response('error', 'Not authorized', status_code=403)
            collab_req.status = 'accepted'
            collab_req.save()
            Notification.objects.create(
                recipient=collab_req.from_user,
                title="Collaboration Accepted",
                message=f"{request.user.full_name} accepted your collaboration request for '{collab_req.event.title}'.",
                notification_type="collaboration_accepted",
                related_id=collab_req.event.id
            )
            return api_response('success', 'Request accepted')

        elif action == 'reject':
             if collab_req.to_user != request.user:
                return api_response('error', 'Not authorized', status_code=403)
             collab_req.status = 'rejected'
             collab_req.save()
             Notification.objects.create(
                 recipient=collab_req.from_user,
                 title="Collaboration Rejected",
                 message=f"{request.user.full_name} rejected your collaboration request for '{collab_req.event.title}'.",
                 notification_type="collaboration_rejected",
                 related_id=collab_req.event.id
             )
             return api_response('success', 'Request rejected')

        elif action == 'remove':
             if request.user == collab_req.from_user or request.user == collab_req.to_user:
                 collab_req.delete()
                 return api_response('success', 'Collaboration removed')
             return api_response('error', 'Not authorized', status_code=403)

        return api_response('error', 'Invalid action', status_code=400)

class UserCollaborationRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        sent_requests = CollaborationRequest.objects.filter(from_user=request.user).order_by('-created_at')
        received_requests = CollaborationRequest.objects.filter(to_user=request.user).order_by('-created_at')

        return api_response('success', 'Collaboration requests', {
            'sent': CollaborationRequestSerializer(sent_requests, many=True).data,
            'received': CollaborationRequestSerializer(received_requests, many=True).data
        })

class BaseUserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_type = self.user_type
        queryset = User.objects.filter(user_type=user_type, is_active=True).exclude(host_name__isnull=True).exclude(host_name__exact='').order_by('-date_joined')
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) | 
                Q(host_name__icontains=search)
            )
        
        # Category Filter
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(host_category_id=category_id)
            
        return queryset

class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

class NotificationMarkAllAsReadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return api_response('success', 'All notifications marked as read', {})

class ArtistListAPIView(BaseUserListAPIView):
    user_type = 'artist'

class VenueListAPIView(BaseUserListAPIView):
    user_type = 'venue_owner'

class ExperienceProviderListAPIView(BaseUserListAPIView):
    user_type = 'experience_provider'

class AdminCreatedEventListAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        today = timezone.now().date()
        # Enforce approved and future events
        queryset = Event.objects.filter(owner__is_staff=True, status='approved', event_date__gte=today).order_by('-id')
        
        # Manual Category Filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
            
        return queryset



class MyUpcomingEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()
        
        # 1. Upcoming Owned Events
        q_owned = Q(owner=user) & Q(event_date__gte=today)
        
        # Combine
        queryset = Event.objects.filter(q_owned).distinct().order_by('event_date')
        
        # Manual Category Filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset

class MyPastEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None # No pagination, fixed limit

    def get_queryset(self):
        user = self.request.user
        today = timezone.now().date()
        
        # 1. Past Owned Requests (Past date OR status finished)
        q_owned = Q(owner=user) & (Q(event_date__lt=today) | Q(status='finished'))
        
        # Combine
        queryset = Event.objects.filter(q_owned).distinct().order_by('-event_date')
        
        return queryset

class UserUpcomingEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny] # Allow public to see other's upcoming events?
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'category__name']

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
             return Event.objects.none()
             
        user = get_object_or_404(User, id=user_id)
        today = timezone.now().date()
        
        # Public User Events:
        # 1. Owned + Approved + Upcoming
        # 2. Collaborative (Accepted) + Approved + Upcoming
        
        q_owned = Q(owner=user)
        q_collab = Q(collaboration_requests__to_user=user, collaboration_requests__status='accepted')
        
        q_filter = (q_owned | q_collab) & Q(status='approved', event_date__gte=today)
        
        queryset = Event.objects.filter(q_filter).distinct().order_by('event_date')
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset

class UserPastEventsAPIView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if not user_id:
             return Event.objects.none()
             
        user = get_object_or_404(User, id=user_id)
        today = timezone.now().date()
        
        # Public User Events = Only details they OWN and are APPROVED/FINISHED
        queryset = Event.objects.filter(
            Q(owner=user) & 
            Q(status__in=['approved', 'finished']) &
            (Q(event_date__lt=today) | Q(status='finished'))
        ).order_by('-event_date')
        
        return queryset

from .models import EventEditHistory, EventUpdateNotification
class EventSensitiveUpdateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
        except Event.DoesNotExist:
             return api_response('error', 'Event not found', status_code=404)

        if event.owner != request.user:
            return api_response('error', 'You are not the owner of this event', status_code=403)

        if not event.can_edit_sensitive_data:
            return api_response('error', 'Sensitive edit is not enabled by admin.', status_code=403)

        serializer = EventSensitiveUpdateSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            # Track changes
            old_data = {
                field: getattr(event, field) for field in serializer.validated_data.keys()
            }
            
            updated_event = serializer.save()
            
            # Log History and Notify
            changes = []
            for field, new_value in serializer.validated_data.items():
                old_val = old_data.get(field)
                if old_val != new_value:
                    # Format value for display
                    old_str = str(old_val)
                    new_str = str(new_value)
                    changes.append(f"{field.replace('_', ' ').title()}")
                    
                    EventEditHistory.objects.create(
                        event=event,
                        field_name=field,
                        old_value=old_str,
                        new_value=new_str,
                        changed_by=request.user
                    )
            
            if changes:
                # Notify booked users
                bookings = Booking.objects.filter(event=event, status='booked')
                user_ids = bookings.values_list('user_id', flat=True).distinct()
                
                change_list = ", ".join(changes)
                message = f"Important Update: The following details for event '{event.title}' have changed: {change_list}. Please check the event page for new details."
                
                notifications = [
                    EventUpdateNotification(
                        event=event,
                        user_id=uid,
                        message=message
                    ) for uid in user_ids
                ]
                EventUpdateNotification.objects.bulk_create(notifications)
            
            # Disable sensitive edit after successful update
            updated_event.can_edit_sensitive_data = False
            updated_event.save()
            
            return api_response('success', 'Event updated successfully', serializer.data)
        
        return api_response('error', 'Validation failed', serializer.errors, status_code=400)

class UserEventUpdateNotificationListAPIView(generics.ListAPIView):
    serializer_class = EventUpdateNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Return notifications for the current user, newest first
        return EventUpdateNotification.objects.filter(user=self.request.user).order_by('-created_at')

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DeleteView
from django.shortcuts import render, redirect
from .models import ContactMessage

class ContactUsView(View):
    def get(self, request):
        return render(request, 'events/contact.html')

    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        msg = request.POST.get('message')
        
        if name and email and subject and msg:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=msg)
            messages.success(request, 'Thank you! Your message has been sent successfully.')
        return redirect('contact_us')


class AdminContactMessageListView(LoginRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'events/admin/contact_message_list.html'
    context_object_name = 'contact_messages'
    paginate_by = 20
    ordering = ['-created_at']
    login_url = 'admin_login'

class AdminContactMessageDeleteView(LoginRequiredMixin, DeleteView):
    model = ContactMessage
    success_url = reverse_lazy('admin_contact_message_list')
    login_url = 'admin_login'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Contact message deleted successfully.")
        return super().delete(request, *args, **kwargs)
