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


class VolunteerSignUp(models.Model):
    """Public volunteer sign-up form submission."""
    REGION_CHOICES = [
        ('tc', 'Twin Cities'),
        ('gmn', 'Greater MN'),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=10, choices=REGION_CHOICES)
    availability = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

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
