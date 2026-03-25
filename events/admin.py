from django.contrib import admin
from .models import User, Event, EventCategory, Booking, ScratchCard, WalletTransaction, EventPrize, HostRequest, ScratchPrize

admin.site.register(User)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'can_edit_sensitive_data', 'created_at')
    list_filter = ('status', 'can_edit_sensitive_data', 'event_date')
    search_fields = ('title', 'owner__full_name')
    list_editable = ('can_edit_sensitive_data',)

admin.site.register(Event, EventAdmin)
from .models import EventEditHistory, EventUpdateNotification
admin.site.register(EventEditHistory)
admin.site.register(EventUpdateNotification)
admin.site.register(EventCategory)
admin.site.register(Booking)
admin.site.register(ScratchCard)
admin.site.register(WalletTransaction)
admin.site.register(EventPrize)
admin.site.register(HostRequest)
admin.site.register(ScratchPrize)
