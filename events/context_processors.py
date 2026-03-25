from .models import HostRequest, Event

def admin_counts(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.user_type == 'admin'):
        return {
            'pending_host_requests': HostRequest.objects.filter(status='pending').count(),
            'pending_events': Event.objects.filter(status='pending').count(),
        }
    return {}
