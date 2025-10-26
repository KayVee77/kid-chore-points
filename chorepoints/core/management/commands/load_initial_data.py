"""
Management command to load initial setup data for ChorePoints system.
This creates the parent user, kids, chores, and rewards from CSV files.

Usage:
    python manage.py load_initial_data
    python manage.py load_initial_data --reset  # Clears existing data first
"""
import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from core.models import Kid, Chore, Reward

User = get_user_model()


class Command(BaseCommand):
    help = 'Load initial data: parent user, kids, chores, and rewards from CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing data before loading',
        )
        parser.add_argument(
            '--parent-username',
            type=str,
            default='tevai',
            help='Username for parent account (default: tevai)',
        )
        parser.add_argument(
            '--parent-password',
            type=str,
            default='tevai123',
            help='Password for parent account (default: tevai123)',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        parent_username = options['parent_username']
        parent_password = options['parent_password']

        if reset:
            self.stdout.write(self.style.WARNING('Deleting existing data...'))
            with transaction.atomic():
                Reward.objects.all().delete()
                Chore.objects.all().delete()
                Kid.objects.all().delete()
                User.objects.filter(username=parent_username).delete()
            self.stdout.write(self.style.SUCCESS('✓ Existing data cleared'))

        # Create or get parent user
        with transaction.atomic():
            parent, created = User.objects.get_or_create(
                username=parent_username,
                defaults={
                    'email': f'{parent_username}@example.com',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if created:
                parent.set_password(parent_password)
                parent.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Created parent user: {parent_username}'))
                self.stdout.write(self.style.WARNING(f'  Password: {parent_password}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Parent user already exists: {parent_username}'))

        # Create kids
        kids_data = [
            {'name': 'Elija', 'pin': '1234', 'emoji': '🚀'},
            {'name': 'Agota', 'pin': '1234', 'emoji': '🌸'},
        ]

        with transaction.atomic():
            for kid_data in kids_data:
                kid, created = Kid.objects.get_or_create(
                    name=kid_data['name'],
                    parent=parent,
                    defaults={
                        'pin': kid_data['pin'],
                        'avatar_emoji': kid_data['emoji'],
                        'points_balance': 0,
                        'map_position': 0,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created kid: {kid_data["name"]} (PIN: {kid_data["pin"]})'))
                else:
                    self.stdout.write(f'  Kid already exists: {kid_data["name"]}')

        # Load chores from CSV
        chores_file = Path(__file__).parent.parent.parent.parent / 'initial_data' / 'Darbai__5_8_m_____prad_ios_paketas.csv'
        
        if chores_file.exists():
            with transaction.atomic():
                with open(chores_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    chore_count = 0
                    for row in reader:
                        # Map difficulty to emoji
                        emoji_map = {
                            'lengva': '🟢',
                            'vidutinė': '🟡',
                            'didelė': '🔴',
                        }
                        emoji = emoji_map.get(row['sudėtingumas'], '⚪')
                        
                        chore, created = Chore.objects.get_or_create(
                            title=row['pavadinimas'],
                            parent=parent,
                            defaults={
                                'points': int(row['taškai']),
                                'icon_emoji': emoji,
                                'active': True,
                            }
                        )
                        if created:
                            chore_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded {chore_count} chores from CSV'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Chores CSV not found: {chores_file}'))

        # Load rewards from CSV
        rewards_file = Path(__file__).parent.parent.parent.parent / 'initial_data' / 'Apdovanojimai___prad_ios_paketas.csv'
        
        if rewards_file.exists():
            with transaction.atomic():
                with open(rewards_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    reward_count = 0
                    for row in reader:
                        # Map type to emoji
                        emoji_map = {
                            'daiktinis': '🎁',
                            'patirtis': '🌟',
                            'privilegija': '👑',
                        }
                        emoji = emoji_map.get(row['tipas'], '🎯')
                        
                        reward, created = Reward.objects.get_or_create(
                            title=row['pavadinimas'],
                            parent=parent,
                            defaults={
                                'cost_points': int(row['taškai']),
                                'icon_emoji': emoji,
                                'active': True,
                            }
                        )
                        if created:
                            reward_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'✓ Loaded {reward_count} rewards from CSV'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Rewards CSV not found: {rewards_file}'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Initial Data Loaded Successfully ==='))
        self.stdout.write(f'Parent: {parent_username} (password: {parent_password})')
        self.stdout.write(f'Kids: Elija, Agota (PIN: 1234)')
        self.stdout.write(f'Chores: {Chore.objects.filter(parent=parent).count()}')
        self.stdout.write(f'Rewards: {Reward.objects.filter(parent=parent).count()}')
        self.stdout.write('\nLogin URLs:')
        self.stdout.write('  Admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('  Kids: http://127.0.0.1:8000/kid/login/')
