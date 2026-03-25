from django import forms
from .models import Event

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def to_python(self, data):
        if not data:
            return None
        if not isinstance(data, list):
            if hasattr(data, 'read'): # It's a single file
                return [data]
            return None
        return data

    def clean(self, data, initial=None):
        if not data and not self.required:
            return []
        if not data and self.required:
             raise forms.ValidationError(self.error_messages['required'])
        
        # If we have data, standard FileField clean only expects one file.
        # We must validate manually or trick it.
        # Simplest is to return data if it looks like a list of files.
        return data

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'category', 'location', 'location_url', 'event_date', 'booking_expiry_date', 'start_time', 'duration', 
            'description', 'collaborator_invite', 'artist_performer', 
            'description', 'collaborator_invite', 'artist_performer', 
            'payment_type', 'regular_price', 'offer_price', 'payment_link', 'maximum_capacity',
            'banner_image', 'terms_document', 'extra_text',
            'attendee_coins', 'scratch_prizes'
            # Note: Gallery images are a separate model, so they are not included in the main form.
            # We would need a formset/separate section for them.
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Event Title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Location'}),
            'location_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Google Maps URL or similar'}),
            'event_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'booking_expiry_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'start_time': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 21:00 - 02:00'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., 5 Hours'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Event Description'}),
            'collaborator_invite': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Collaborator Info'}),
            'artist_performer': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Artist/Performer'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'regular_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'offer_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'payment_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'maximum_capacity': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0 for unlimited'}),
            'banner_image': forms.FileInput(attrs={'class': 'form-file'}),
            'terms_document': forms.FileInput(attrs={'class': 'form-file'}),
            'extra_text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Extra Details'}),
            'attendee_coins': forms.NumberInput(attrs={'class': 'form-input'}),
            'scratch_prizes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Comma separated prizes'}),
        }
    
    gallery_images = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-file', 'multiple': True}),
        required=False,
        label='Gallery Images (Multiple)'
    )
