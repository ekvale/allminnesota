"""
Management command: create staff users Sean, Kuha, Emily with a default password.
Run: python manage.py create_staff_users
Uses get_or_create so safe to run multiple times. Does not overwrite existing passwords.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_PASSWORD = 'allminnesota2025'

STAFF_USERS = [
    {'username': 'sean', 'first_name': 'Sean', 'last_name': ''},
    {'username': 'kuha', 'first_name': 'Kuha', 'last_name': ''},
    {'username': 'emily', 'first_name': 'Emily', 'last_name': ''},
]


class Command(BaseCommand):
    help = 'Create staff users (Sean, Kuha, Emily) with default password.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default=DEFAULT_PASSWORD,
            help=f'Password to set (default: {DEFAULT_PASSWORD})',
        )

    def handle(self, *args, **options):
        password = options['password']
        for u in STAFF_USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'first_name': u['first_name'],
                    'last_name': u.get('last_name', ''),
                    'email': f"{u['username']}@allminnesota.org",
                    'is_staff': True,
                    'is_active': True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created staff user: {user.username} ({user.get_full_name() or user.username})'))
            else:
                self.stdout.write(f'Staff user already exists: {user.username} (password unchanged)')
        self.stdout.write(self.style.WARNING(f'Default password: {password} — users should change it after first login.'))
