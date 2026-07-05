from django.core.management.base import BaseCommand

from accounts.models import Users

# Dummy accounts for testing. Passwords are simple on purpose.
DUMMY_USERS = [
    # Customers
    {'email': 'bobert@wavebar.com',  'full_name': 'Bobert BARatheon',  'role': 'customer',
     'bar_name': 'Storms End Beach Bar', 'bar_location': 'Rhodes',   'phone': '+30 6900 111111',
     'password': 'bobert123'},
    {'email': 'anakin@wavebar.com',  'full_name': 'Anakin Johnwalker', 'role': 'customer',
     'bar_name': 'Tatooine Tiki',        'bar_location': 'Mykonos',  'phone': '+30 6900 222222',
     'password': 'anakin123'},
    # Employees
    {'email': 'mace@wavebar.com',    'full_name': 'Mace Mojito',       'role': 'employee',
     'bar_name': '', 'bar_location': '', 'phone': '+30 6900 333333',
     'password': 'mace1234'},
    {'email': 'quigon@wavebar.com',  'full_name': 'Quigon Gin',        'role': 'employee',
     'bar_name': '', 'bar_location': '', 'phone': '+30 6900 444444',
     'password': 'quigon123'},
    # Admin (also a Django superuser so /admin/ is reachable)
    {'email': 'darth@wavebar.com',   'full_name': 'Darth Drinker',     'role': 'admin',
     'bar_name': '', 'bar_location': '', 'phone': '+30 6900 555555',
     'password': 'darth1234', 'is_staff': True, 'is_superuser': True},
]


class Command(BaseCommand):
    help = 'Create dummy users (customers, employees, admin) for testing.'

    def handle(self, *args, **options):
        for data in DUMMY_USERS:
            data = dict(data)              # copy so we don't mutate the template
            email = data['email']
            if Users.objects.filter(email=email).exists():
                self.stdout.write(f'  skipped (exists): {email}')
                continue
            Users.objects.create_user(**data)
            self.stdout.write(self.style.SUCCESS(
                f"  created {data['role']}: {data['full_name']} <{email}>"))
        self.stdout.write('Done.')
