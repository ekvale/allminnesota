"""
Django admin registration for All Minnesota models.
Includes distribution sites, donations, food orders, meal kit distributions, partners.
"""

from django.contrib import admin
from .models import (
    FundraisingGoal,
    Event,
    VolunteerSignUp,
    ContactMessage,
    ImpactUpdate,
    DistributionSite,
    Donation,
    FoodOrder,
    MealKitDistribution,
    PartnerOrganization,
    PartnerContact,
)


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


@admin.register(DistributionSite)
class DistributionSiteAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'city_state', 'capacity_meals', 'capacity_volunteers',
        'is_active', 'updated_at',
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'city_state', 'address']


@admin.register(VolunteerSignUp)
class VolunteerSignUpAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'email', 'region',
        'site', 'status', 'submitted_at',
    ]
    list_filter = ['status', 'region']
    search_fields = ['first_name', 'last_name', 'email']
    raw_id_fields = ['site']


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


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
        'amount', 'received_at', 'donor_name', 'source',
        'recorded_at', 'recorded_by',
    ]
    list_filter = ['source']
    search_fields = ['donor_name', 'note']
    date_hierarchy = 'received_at'


@admin.register(FoodOrder)
class FoodOrderAdmin(admin.ModelAdmin):
    list_display = [
        'supplier', 'order_date', 'total_cost', 'status',
        'site', 'ordered_by', 'created_at',
    ]
    list_filter = ['status']
    search_fields = ['supplier', 'description']
    raw_id_fields = ['site', 'ordered_by']
    date_hierarchy = 'order_date'


@admin.register(MealKitDistribution)
class MealKitDistributionAdmin(admin.ModelAdmin):
    list_display = [
        'distribution_date', 'site', 'meal_kits_count', 'format',
        'recorded_at', 'recorded_by',
    ]
    list_filter = ['format']
    raw_id_fields = ['site', 'recorded_by']
    date_hierarchy = 'distribution_date'


class PartnerContactInline(admin.TabularInline):
    model = PartnerContact
    extra = 1


@admin.register(PartnerOrganization)
class PartnerOrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'org_type', 'phone', 'email', 'is_active', 'updated_at']
    list_filter = ['org_type', 'is_active']
    search_fields = ['name', 'email', 'notes']
    inlines = [PartnerContactInline]


@admin.register(PartnerContact)
class PartnerContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'role', 'email', 'phone', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['name', 'email']
    raw_id_fields = ['partner']
