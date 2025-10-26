"""
Management command to load initial setup data for ChorePoints system.
This creates admin users, kids, chores, and rewards from JSON/CSV files.

Usage:
    python manage.py load_initial_data
    python manage.py load_initial_data --reset  # Clears existing data first

Edit initial_data/ files to customize:
    - users.json: Admin users and kids
    - chores.csv: Available chores with points and emojis
    - rewards.csv: Available rewards with costs and emojis
"""
import csv
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import Kid, Chore, Reward

User = get_user_model()


class Command(BaseCommand):
    help = 'Load initial data from JSON/CSV files in initial_data/ folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing data before loading',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        
        # Get initial_data folder path
        data_folder = Path(__file__).parent.parent.parent.parent / 'initial_data'
        users_file = data_folder / 'users.json'
        chores_file = data_folder / 'chores.csv'
        rewards_file = data_folder / 'rewards.csv'
        
        # Check if files exist
        if not users_file.exists():
            self.stdout.write(self.style.ERROR(f'✗ users.json not found: {users_file}'))
            return
        
        if reset:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            with transaction.atomic():
                Reward.objects.all().delete()
                Chore.objects.all().delete()
                Kid.objects.all().delete()
                # Only delete users that are in the users.json file
                with open(users_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                    for user_data in users_data.get('admin_users', []):
                        User.objects.filter(username=user_data['username']).delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))
        
        # Load users from JSON
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        # Create admin users
        created_admins = []
        with transaction.atomic():
            for user_data in users_data.get('admin_users', []):
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data.get('email', f"{user_data['username']}@example.com"),
                        'is_staff': user_data.get('is_staff', True),
                        'is_superuser': user_data.get('is_superuser', True),
                    }
                )
                if created:
                    user.set_password(user_data.get('password', 'changeme123'))
                    user.save()
                    created_admins.append(user_data)
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created admin: {user_data["username"]} (password: {user_data.get("password", "changeme123")})'
                    ))
                else:
                    self.stdout.write(f'  Admin already exists: {user_data["username"]}')
        
        # Get the first admin as default parent for kids
        if not User.objects.filter(is_staff=True).exists():
            self.stdout.write(self.style.ERROR('✗ No admin users found. Cannot create kids.'))
            return
        
        default_parent = User.objects.filter(is_staff=True).first()
        
        # Create kids
        created_kids = []
        with transaction.atomic():
            for kid_data in users_data.get('kids', []):
                kid, created = Kid.objects.get_or_create(
                    name=kid_data['name'],
                    parent=default_parent,
                    defaults={
                        'pin': kid_data.get('pin', '1234'),
                        'avatar_emoji': kid_data.get('avatar_emoji', '😊'),
                        'map_theme': kid_data.get('map_theme', 'ISLAND'),
                        'points_balance': 0,
                        'map_position': 0,
                    }
                )
                if created:
                    created_kids.append(kid_data)
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Created kid: {kid_data["name"]} {kid_data.get("avatar_emoji", "")} (PIN: {kid_data.get("pin", "1234")})'
                    ))
                else:
                    self.stdout.write(f'  Kid already exists: {kid_data["name"]}')
        
        # Load chores from CSV
        if chores_file.exists():
            with transaction.atomic():
                with open(chores_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    chore_count = 0
                    for row in reader:
                        chore, created = Chore.objects.get_or_create(
                            title=row['title'],
                            parent=default_parent,
                            defaults={
                                'points': int(row['points']),
                                'icon_emoji': row.get('icon_emoji', '✓'),
                                'active': True,
                            }
                        )
                        if created:
                            chore_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded {chore_count} chores from CSV'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Chores CSV not found: {chores_file}'))
        
        # Load rewards from CSV
        if rewards_file.exists():
            with transaction.atomic():
                with open(rewards_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    reward_count = 0
                    for row in reader:
                        reward, created = Reward.objects.get_or_create(
                            title=row['title'],
                            parent=default_parent,
                            defaults={
                                'cost_points': int(row['cost_points']),
                                'icon_emoji': row.get('icon_emoji', '🎁'),
                                'active': True,
                            }
                        )
                        if created:
                            reward_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded {reward_count} rewards from CSV'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Rewards CSV not found: {rewards_file}'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Initial Data Loaded Successfully ==='))
        
        if created_admins:
            self.stdout.write('\nAdmin Users:')
            for admin in created_admins:
                self.stdout.write(f'  • {admin["username"]} (password: {admin.get("password", "changeme123")})')
        
        if created_kids:
            self.stdout.write('\nKids:')
            for kid in created_kids:
                self.stdout.write(f'  • {kid["name"]} {kid.get("avatar_emoji", "")} (PIN: {kid.get("pin", "1234")})')
        
        total_chores = Chore.objects.filter(parent=default_parent).count()
        total_rewards = Reward.objects.filter(parent=default_parent).count()
        
        self.stdout.write(f'\nChores: {total_chores}')
        self.stdout.write(f'Rewards: {total_rewards}')
        
        self.stdout.write('\nLogin URLs:')
        self.stdout.write('  Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  Kids: http://127.0.0.1:8000/kid/login/')
