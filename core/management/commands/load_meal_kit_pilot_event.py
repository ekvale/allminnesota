"""
Management command: add Meal Kit Program Pilot Launch event (last weekend of February)
at Indigenous Food Lab, with meal kit image.
Run: python manage.py load_meal_kit_pilot_event
Uses get_or_create so safe to run multiple times. Copies image from static to media.
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event


# Last Saturday of February for the given year (Python weekday: Monday=0, Saturday=5)
def last_saturday_february(year):
    last_day = 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    d = datetime(year, 2, last_day)
    days_back = (d.weekday() - 5 + 7) % 7  # 0 if already Saturday
    d = d - timedelta(days=days_back)
    d = d.replace(hour=10, minute=0, second=0, microsecond=0)
    return timezone.make_aware(d)


class Command(BaseCommand):
    help = 'Add Meal Kit Program Pilot Launch event (last weekend of February) at Indigenous Food Lab.'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=2026, help='Year (default: 2026)')

    def handle(self, *args, **options):
        year = options['year']
        event_date = last_saturday_february(year)

        base_dir = Path(settings.BASE_DIR)
        static_image = base_dir / 'core' / 'static' / 'core' / 'images' / 'events' / 'meal_kit_pilot.png'
        media_root = Path(settings.MEDIA_ROOT)
        events_media = media_root / 'events'
        events_media.mkdir(parents=True, exist_ok=True)
        dest_image = events_media / 'meal_kit_pilot.png'

        if static_image.exists():
            shutil.copy2(static_image, dest_image)
            self.stdout.write(self.style.SUCCESS(f'Copied image to {dest_image}'))
        else:
            self.stdout.write(self.style.WARNING(f'Source image not found at {static_image}; event will have no image.'))

        title_final = 'Meal Kit Program Pilot Launch'
        event = Event.objects.filter(title=title_final).first()
        if not event:
            event = Event.objects.create(
                title=title_final,
                date=event_date,
                venue_name='Indigenous Food Lab',
                venue_address='920 E. Lake Street, #107, Midtown Global Market',
                city_state='Minneapolis, MN 55407',
                description=(
                    'Join us for the pilot launch of our meal kit program. '
                    'Fresh, pre-portioned ingredients and recipes for cooking at home, '
                    'in partnership with Indigenous Food Lab at Midtown Global Market.'
                ),
                ticket_url='',
                is_published=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Created event: {event.title} on {event.date.date()}'))
        else:
            self.stdout.write(f'Event already exists: {event.title}')

        if dest_image.exists() and not event.image:
            event.image = 'events/meal_kit_pilot.png'
            event.save(update_fields=['image'])
            self.stdout.write(self.style.SUCCESS('Attached meal kit image to event.'))

        if not event.is_published:
            event.is_published = True
            event.save(update_fields=['is_published'])
            self.stdout.write(self.style.SUCCESS('Published event.'))

        if getattr(event.date, 'tzinfo', None) is None:
            event.date = timezone.make_aware(event.date)
            event.save(update_fields=['date'])
            self.stdout.write(self.style.SUCCESS('Fixed event date to be timezone-aware.'))

        self.stdout.write(self.style.SUCCESS('Done.'))
