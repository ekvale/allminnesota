"""
Management command: load likely partner organizations and distribution sites
for All Minnesota (Minnesota hunger relief, food banks, meal distribution).
Run: python manage.py load_partner_organizations
Uses get_or_create so safe to run multiple times.
"""

from django.core.management.base import BaseCommand
from core.models import PartnerOrganization, DistributionSite


# Partner organizations (food banks, hunger relief, meal distribution) — research from web
PARTNERS = [
    {
        'name': 'Loaves and Fishes Minnesota',
        'org_type': 'distribution_partner',
        'address': 'Multiple community meal sites across 15 counties (130+ outlets). See website for locations.',
        'phone': '612-377-9810',
        'email': 'office@loavesandfishesmn.org',
        'website': 'https://www.loavesandfishesmn.org',
        'notes': 'Serves free, healthy meals to Minnesotans in need. Community meal site locator: loavesandfishesmn.org/find-a-community-meal',
    },
    {
        'name': 'Second Harvest Heartland',
        'org_type': 'distribution_partner',
        'address': '7101 Winnetka Avenue N, Brooklyn Park, MN 55428',
        'phone': '651-484-5117',
        'email': 'info@2harvest.org',
        'website': 'https://www.2harvest.org',
        'notes': 'Distributes ~145 million meals annually across MN and western WI through 1,000+ partner programs. Care Center: 866-844-3663.',
    },
    {
        'name': 'The Food Group',
        'org_type': 'distribution_partner',
        'address': '8501 54th Ave. N, New Hope, MN 55428',
        'phone': '763-450-3860',
        'email': '',
        'website': 'https://www.thefoodgroupmn.org',
        'notes': 'Nonprofit food bank serving 180+ food shelves and meal programs across 30+ counties. St. Paul office: 555 Park St, Suite 400.',
    },
    {
        'name': 'North Country Food Bank',
        'org_type': 'distribution_partner',
        'address': '1011 11th Ave NE, East Grand Forks, MN 56721',
        'phone': '218-399-7356',
        'email': 'info@northcountryfoodbank.org',
        'website': 'https://www.northcountryfoodbank.org',
        'notes': 'Serves 21 counties in northwest and west central MN. 220 agency partners; mobile food pantry, senior nutrition, backpack program.',
    },
    {
        'name': 'Second Harvest Northland',
        'org_type': 'distribution_partner',
        'address': '2302 Commonwealth Avenue, Duluth, MN 55808',
        'phone': '218-727-5653',
        'email': 'info@secondharvestnorthland.org',
        'website': 'https://secondharvestnorthland.org',
        'notes': 'Mobile Food Pantry and food shelf programs across northeastern MN (Aitkin, Carlton, Cass, Cook, Crow Wing, Itasca, Kanabec, Koochiching).',
    },
    {
        'name': 'Hunger Solutions Minnesota',
        'org_type': 'distribution_partner',
        'address': '555 Park Street, Suite 400, St. Paul, MN 55103',
        'phone': '888-711-1151',
        'email': '',
        'website': 'https://www.hungersolutions.org',
        'notes': 'Operates Minnesota Food HelpLine; SNAP assistance, food shelf referrals, find-help map. Now part of The Food Group (2024).',
    },
    {
        'name': 'Feeding Community',
        'org_type': 'distribution_partner',
        'address': '',
        'phone': '',
        'email': '',
        'website': 'https://feeding-community.org',
        'notes': 'Grassroots initiative; distributed 1.2M+ meals to vulnerable community members since 2020.',
    },
    {
        'name': 'White Earth Nation Food Sovereignty Initiative',
        'org_type': 'distribution_partner',
        'address': 'White Earth Nation, Minnesota',
        'phone': '',
        'email': '',
        'website': '',
        'notes': 'Tribal food sovereignty; community potlucks, traditional planting/gathering/harvest. Potential partner for indigenous-led meal distribution.',
    },
    {
        'name': 'Fond du Lac Band - Gitigaaning',
        'org_type': 'distribution_partner',
        'address': 'Fond du Lac Reservation, Minnesota',
        'phone': '',
        'email': '',
        'website': '',
        'notes': '36-acre farm (Gitigaaning) for food sovereignty trainings and food systems rooted in Anishinaabe values. Potential distribution partner.',
    },
]

# Example distribution sites (specific meal sites / locations) — capacity TBD by staff
DISTRIBUTION_SITES = [
    {
        'name': 'Loaves and Fishes - Holy Rosary Catholic Church',
        'address': 'Check loavesandfishesmn.org for current address and hours',
        'city_state': 'Minneapolis, MN',
        'capacity_meals': 0,
        'capacity_volunteers': 0,
        'notes': 'Community meal site (Monday-Thursday). Verify address and capacity on Loaves and Fishes site locator.',
    },
    {
        'name': 'Loaves and Fishes - St. Matthew\'s Catholic Church',
        'address': 'Check loavesandfishesmn.org for current address and hours',
        'city_state': 'St. Paul, MN',
        'capacity_meals': 0,
        'capacity_volunteers': 0,
        'notes': 'Community meal site (Monday-Friday). Verify on Loaves and Fishes site locator.',
    },
    {
        'name': 'Richard M. Schulze Family Foundation Saint Paul Opportunity Center',
        'address': 'Check loavesandfishesmn.org for current address',
        'city_state': 'St. Paul, MN',
        'capacity_meals': 0,
        'capacity_volunteers': 0,
        'notes': 'Community meal site open daily (Sunday-Saturday). Loaves and Fishes.',
    },
    {
        'name': 'Second Harvest Northland - Duluth Distribution Center',
        'address': '2302 Commonwealth Avenue',
        'city_state': 'Duluth, MN 55808',
        'capacity_meals': 0,
        'capacity_volunteers': 0,
        'contact_phone': '218-727-5653',
        'contact_email': 'info@secondharvestnorthland.org',
        'notes': 'Food shelf drive-thru Tue/Fri 10am-1pm. Agency partner for Greater MN.',
    },
    {
        'name': 'North Country Food Bank - East Grand Forks',
        'address': '1011 11th Ave NE',
        'city_state': 'East Grand Forks, MN 56721',
        'capacity_meals': 0,
        'capacity_volunteers': 0,
        'contact_phone': '218-399-7356',
        'contact_email': 'info@northcountryfoodbank.org',
        'notes': 'Warehouse/distribution facility; 35,000 sq ft. Serves 21 counties.',
    },
]


class Command(BaseCommand):
    help = 'Load likely partner organizations and distribution sites for All Minnesota (from web research).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--partners-only',
            action='store_true',
            help='Load only partner organizations, not distribution sites.',
        )
        parser.add_argument(
            '--sites-only',
            action='store_true',
            help='Load only distribution sites, not partners.',
        )

    def handle(self, *args, **options):
        partners_only = options['partners_only']
        sites_only = options['sites_only']

        if not sites_only:
            for p in PARTNERS:
                obj, created = PartnerOrganization.objects.get_or_create(
                    name=p['name'],
                    defaults={
                        'org_type': p['org_type'],
                        'address': p.get('address', ''),
                        'phone': p.get('phone', ''),
                        'email': p.get('email', '') or '',
                        'website': p.get('website', '') or '',
                        'notes': p.get('notes', ''),
                        'is_active': True,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created partner: {obj.name}'))
                else:
                    self.stdout.write(f'Partner already exists: {obj.name}')

        if not partners_only:
            for d in DISTRIBUTION_SITES:
                obj, created = DistributionSite.objects.get_or_create(
                    name=d['name'],
                    defaults={
                        'address': d['address'],
                        'city_state': d['city_state'],
                        'capacity_meals': d.get('capacity_meals', 0),
                        'capacity_volunteers': d.get('capacity_volunteers', 0),
                        'contact_phone': d.get('contact_phone', ''),
                        'contact_email': d.get('contact_email', ''),
                        'notes': d.get('notes', ''),
                        'is_active': True,
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created distribution site: {obj.name}'))
                else:
                    self.stdout.write(f'Distribution site already exists: {obj.name}')

        self.stdout.write(self.style.SUCCESS('Done. Review and edit in Django admin as needed.'))
