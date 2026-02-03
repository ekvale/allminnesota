"""
Management command: load brainstormed early-stage tasks onto the Kanban board.
Run: python manage.py load_initial_tasks
Uses get_or_create on title (within same status) so safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from core.models import Task

# Early-stage tasks: find sites, capacity, volunteers, contact tribes/partners, etc.
INITIAL_TASKS = [
    # Backlog
    {'title': 'Find and list distribution sites and capacity', 'status': 'backlog', 'order': 10,
     'description': 'Identify potential meal kit distribution locations; document address, capacity (meals/volunteers), and contact.'},
    {'title': 'Map sites to regions (Twin Cities vs Greater MN)', 'status': 'backlog', 'order': 9,
     'description': 'Assign each distribution site to a region for volunteer and logistics planning.'},
    {'title': 'Identify kitchen/commissary for meal prep', 'status': 'backlog', 'order': 8,
     'description': 'Find licensed kitchen or commissary space for preparing meal kits.'},
    {'title': 'Define meal kit contents and sourcing', 'status': 'backlog', 'order': 7,
     'description': 'Decide what goes in each kit; source ingredients and packaging.'},
    {'title': 'Create volunteer onboarding materials', 'status': 'backlog', 'order': 6,
     'description': 'Handouts, checklists, or short training for distribution-day volunteers.'},
    {'title': 'Create distribution day runbook', 'status': 'backlog', 'order': 5,
     'description': 'Step-by-step guide for site leads and volunteers on distribution days.'},
    {'title': 'Fundraising outreach (donors, grants)', 'status': 'backlog', 'order': 4,
     'description': 'Identify and contact donors and grant programs to fund meals and operations.'},
    # To Do
    {'title': 'Determine volunteer requirements per site', 'status': 'to_do', 'order': 10,
     'description': 'How many volunteers per site per distribution; roles (setup, check-in, distribution, cleanup).'},
    {'title': 'Contact tribes and tribal programs', 'status': 'to_do', 'order': 9,
     'description': 'Reach out to tribal nations and tribal food/health programs to explore partnership and distribution.'},
    {'title': 'Contact potential partner organizations', 'status': 'to_do', 'order': 8,
     'description': 'Food banks, hunger relief orgs, community centers — discuss partnerships and site use.'},
    {'title': 'Recruit volunteers (outreach)', 'status': 'to_do', 'order': 7,
     'description': 'Promote volunteer sign-up via website, social media, and partner networks.'},
    {'title': 'Set up meal kit ordering process', 'status': 'to_do', 'order': 6,
     'description': 'How sites or partners order meal kits; lead time, quantities, delivery.'},
    {'title': 'Establish delivery schedule and logistics', 'status': 'to_do', 'order': 5,
     'description': 'When and how meal kits get from kitchen to distribution sites.'},
    {'title': 'Finalize partner MOUs / agreements', 'status': 'to_do', 'order': 4,
     'description': 'Memoranda of understanding or simple agreements with distribution and kitchen partners.'},
    {'title': 'Pilot distribution at one site', 'status': 'to_do', 'order': 3,
     'description': 'Run a small pilot at one site to test process before scaling.'},
]


class Command(BaseCommand):
    help = 'Load brainstormed early-stage tasks onto the Kanban board.'

    def handle(self, *args, **options):
        created_count = 0
        for t in INITIAL_TASKS:
            _, created = Task.objects.get_or_create(
                title=t['title'],
                defaults={
                    'description': t.get('description', ''),
                    'status': t['status'],
                    'order': t.get('order', 0),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created task: {t['title']}"))
            else:
                self.stdout.write(f"Task already exists: {t['title']}")
        self.stdout.write(self.style.SUCCESS(f'Done. Created {created_count} new task(s).'))
