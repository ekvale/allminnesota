"""
Forms for All Minnesota: volunteer sign-up, contact, goal update, and events.
"""

from django import forms
from .models import VolunteerSignUp, ContactMessage, FundraisingGoal, Event, Task


class VolunteerForm(forms.ModelForm):
    """ModelForm for VolunteerSignUp (all fields except submitted_at)."""
    class Meta:
        model = VolunteerSignUp
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'region', 'availability', 'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone (optional)'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'availability': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'When are you available?'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any notes?'}),
        }


class ContactForm(forms.ModelForm):
    """ModelForm for ContactMessage (all fields except submitted_at)."""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your message'}),
        }


class GoalUpdateForm(forms.ModelForm):
    """ModelForm for FundraisingGoal (only: current_amount, meals_funded, volunteers_count)."""
    class Meta:
        model = FundraisingGoal
        fields = ['current_amount', 'meals_funded', 'volunteers_count']
        widgets = {
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'meals_funded': forms.NumberInput(attrs={'class': 'form-control'}),
            'volunteers_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class EventForm(forms.ModelForm):
    """ModelForm for Event (all fields)."""
    class Meta:
        model = Event
        fields = [
            'title', 'date', 'venue_name', 'venue_address', 'city_state',
            'description', 'ticket_url', 'image', 'is_published',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'venue_name': forms.TextInput(attrs={'class': 'form-control'}),
            'venue_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city_state': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'ticket_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'External ticket link'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accept HTML datetime-local format (no seconds)
        self.fields['date'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']


class TaskForm(forms.ModelForm):
    """ModelForm for Task (create/edit)."""
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'assigned_to', 'due_date', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = VolunteerSignUp.objects.all().order_by('first_name', 'last_name')
        self.fields['assigned_to'].queryset = qs
        self.fields['assigned_to'].required = False
        # Show volunteer name (not pk) in the dropdown
        self.fields['assigned_to'].label_from_instance = lambda obj: f'{obj.first_name} {obj.last_name}'
        self.fields['assigned_to'].empty_label = '— No one —'


class TaskStatusForm(forms.Form):
    """Quick-move form for kanban: change task status only."""
    status = forms.ChoiceField(choices=Task.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))
