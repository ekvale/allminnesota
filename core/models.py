"""
Models for All Minnesota: fundraising goals, events, volunteer sign-ups,
contact messages, and impact updates.
"""

from decimal import Decimal
from django.db import models
from django.conf import settings


class FundraisingGoal(models.Model):
    """Single active fundraising campaign with target and current amounts."""
    goal_title = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    meals_funded = models.IntegerField(default=0)
    volunteers_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fundraising Goal'
        verbose_name_plural = 'Fundraising Goals'

    def __str__(self):
        return self.goal_title


class Event(models.Model):
    """Community event with optional external ticket link (no payment on site)."""
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    venue_name = models.CharField(max_length=200)
    venue_address = models.TextField()
    city_state = models.CharField(max_length=100)
    description = models.TextField()
    ticket_url = models.URLField(blank=True)  # EXTERNAL link only
    image = models.ImageField(upload_to='events/', blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.title


class DistributionSite(models.Model):
    """Distribution site where meal kits are delivered; has capacity for meals and volunteers."""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city_state = models.CharField(max_length=100)
    capacity_meals = models.PositiveIntegerField(
        default=0,
        help_text='Max meal kits per distribution (0 = not set)',
    )
    capacity_volunteers = models.PositiveIntegerField(
        default=0,
        blank=True,
        help_text='Max volunteers at site (0 = not set)',
    )
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Distribution Site'
        verbose_name_plural = 'Distribution Sites'

    def __str__(self):
        return self.name


class VolunteerSignUp(models.Model):
    """Public volunteer sign-up form submission; can be assigned to a distribution site."""
    REGION_CHOICES = [
        ('tc', 'Twin Cities'),
        ('gmn', 'Greater MN'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('inactive', 'Inactive'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=10, choices=REGION_CHOICES)
    availability = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    # Backend: assign volunteer to a site and track status
    site = models.ForeignKey(
        DistributionSite,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteers',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Volunteer Sign-Up'
        verbose_name_plural = 'Volunteer Sign-Ups'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ContactMessage(models.Model):
    """Public contact form submission."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return self.subject


class ImpactUpdate(models.Model):
    """Admin-recorded snapshot of impact (amount raised, meals, volunteers)."""
    amount_raised = models.DecimalField(max_digits=10, decimal_places=2)
    meals_funded = models.IntegerField()
    volunteers = models.IntegerField()
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='impact_updates',
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Impact Update'
        verbose_name_plural = 'Impact Updates'

    def __str__(self):
        return f'${self.amount_raised} @ {self.updated_at}'


class Donation(models.Model):
    """Record of a donation received (no payment processing on site)."""
    SOURCE_CHOICES = [
        ('check', 'Check'),
        ('online', 'Online / external'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    received_at = models.DateField()
    donor_name = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')
    note = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donations_recorded',
    )

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Donation'
        verbose_name_plural = 'Donations'

    def __str__(self):
        return f'${self.amount} ({self.received_at})'


class FoodOrder(models.Model):
    """Record of a food/supply order placed (wholesale, for distribution)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    order_date = models.DateField()
    supplier = models.CharField(max_length=200)
    description = models.TextField(help_text='Items ordered or notes')
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    site = models.ForeignKey(
        DistributionSite,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='food_orders',
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ordered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='food_orders_placed',
    )

    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Food Order'
        verbose_name_plural = 'Food Orders'

    def __str__(self):
        return f'{self.supplier} ({self.order_date})'


class MealKitDistribution(models.Model):
    """Record of meal kit distribution: raw or partially prepared with recipe cards."""
    FORMAT_CHOICES = [
        ('raw', 'Raw ingredients'),
        ('partially_prepared', 'Partially prepared with recipe cards'),
    ]
    distribution_date = models.DateField()
    site = models.ForeignKey(
        DistributionSite,
        on_delete=models.CASCADE,
        related_name='meal_kit_distributions',
    )
    meal_kits_count = models.PositiveIntegerField()
    format = models.CharField(
        max_length=30,
        choices=FORMAT_CHOICES,
        default='raw',
        help_text='Raw ingredients or partially prepared with recipe cards',
    )
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meal_kit_distributions_recorded',
    )

    class Meta:
        ordering = ['-distribution_date']
        verbose_name = 'Meal Kit Distribution'
        verbose_name_plural = 'Meal Kit Distributions'

    def __str__(self):
        return f'{self.site.name} — {self.distribution_date} ({self.meal_kits_count} kits)'


class PartnerOrganization(models.Model):
    """Partner organization (supplier, distribution partner, etc.)."""
    ORG_TYPE_CHOICES = [
        ('supplier', 'Supplier'),
        ('distribution_partner', 'Distribution partner'),
        ('funder', 'Funder'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    org_type = models.CharField(max_length=30, choices=ORG_TYPE_CHOICES, default='other')
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Partner Organization'
        verbose_name_plural = 'Partner Organizations'

    def __str__(self):
        return self.name


class PartnerContact(models.Model):
    """Contact person at a partner organization."""
    partner = models.ForeignKey(
        PartnerOrganization,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['partner', 'name']
        verbose_name = 'Partner Contact'
        verbose_name_plural = 'Partner Contacts'

    def __str__(self):
        return f'{self.name} — {self.partner.name}'
