"""
Management command: add Keith Secola event (first Saturday of March, TBD location)
and attach the portrait image.
Run: python manage.py load_keith_secola_event
Uses get_or_create so safe to run multiple times. Copies image from static to media.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event


# First Saturday of March for the given year (Python weekday: Monday=0, Saturday=5)
def first_saturday_march(year):
    d = datetime(year, 3, 1)
    days_until_saturday = (5 - d.weekday() + 7) % 7  # 0 if Mar 1 is Sat, else 1–6
    first_sat = d + timedelta(days=days_until_saturday)
    first_sat = first_sat.replace(hour=19, minute=0, second=0, microsecond=0)
    return timezone.make_aware(first_sat)


class Command(BaseCommand):
    help = 'Add Keith Secola event (first Saturday of March, TBD location) with portrait image.'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=2026, help='Year for first Saturday of March (default: 2026)')

    def handle(self, *args, **options):
        year = options['year']
        event_date = first_saturday_march(year)

        # Source image (shipped in repo under static)
        base_dir = Path(settings.BASE_DIR)
        static_image = base_dir / 'core' / 'static' / 'core' / 'images' / 'events' / 'keith_secola.png'
        media_root = Path(settings.MEDIA_ROOT)
        events_media = media_root / 'events'
        events_media.mkdir(parents=True, exist_ok=True)
        dest_image = events_media / 'keith_secola.png'

        if static_image.exists():
            shutil.copy2(static_image, dest_image)
            self.stdout.write(self.style.SUCCESS(f'Copied image to {dest_image}'))
        else:
            self.stdout.write(self.style.WARNING(f'Source image not found at {static_image}; event will have no image.'))

        event, created = Event.objects.get_or_create(
            title='Keith Secola',
            defaults={
                'date': event_date,
                'venue_name': 'TBD',
                'venue_address': 'TBD',
                'city_state': 'TBD',
                'description': (
                    'Join us for an evening with Keith Secola—musician, songwriter, and cultural voice. '
                    'Details and location to be announced.'
                ),
                'ticket_url': '',
                'is_published': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created event: {event.title} on {event.date.date()}'))
        else:
            self.stdout.write(f'Event already exists: {event.title}')

        if dest_image.exists() and not event.image:
            event.image = 'events/keith_secola.png'
            event.save(update_fields=['image'])
            self.stdout.write(self.style.SUCCESS('Attached Keith Secola portrait to event.'))

        if not event.is_published:
            event.is_published = True
            event.save(update_fields=['is_published'])
            self.stdout.write(self.style.SUCCESS('Published event so it appears on the Events page.'))

        # Ensure event date is timezone-aware so it shows in "upcoming" (date__gte=now) queries
        if getattr(event.date, 'tzinfo', None) is None:
            event.date = timezone.make_aware(event.date)
            event.save(update_fields=['date'])
            self.stdout.write(self.style.SUCCESS('Fixed event date to be timezone-aware.'))

        self.stdout.write(self.style.SUCCESS('Done.'))
