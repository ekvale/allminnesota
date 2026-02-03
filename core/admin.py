"""
Django admin registration for All Minnesota models.
All 5 models registered with list_display and search/filter as specified.
"""

from django.contrib import admin
from .models import FundraisingGoal, Event, VolunteerSignUp, ContactMessage, ImpactUpdate


@admin.register(FundraisingGoal)
class FundraisingGoalAdmin(admin.ModelAdmin):
    list_display = [
        'goal_title', 'target_amount', 'current_amount',
        'meals_funded', 'volunteers_count', 'last_updated',
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'venue_name', 'is_published']
    list_filter = ['is_published']


@admin.register(VolunteerSignUp)
class VolunteerSignUpAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'region', 'submitted_at']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at']
    search_fields = ['name', 'email', 'subject']


@admin.register(ImpactUpdate)
class ImpactUpdateAdmin(admin.ModelAdmin):
    list_display = [
        'amount_raised', 'meals_funded', 'volunteers',
        'updated_at', 'updated_by',
    ]
