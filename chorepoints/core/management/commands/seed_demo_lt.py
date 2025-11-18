from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.models import Kid, Chore, Reward
import csv
from pathlib import Path

KIDS = [
    ("Elija", "ISLAND", "F"),  # Girl
    ("Agota", "SPACE", "F"),   # Girl
]
PIN = "1234"

class Command(BaseCommand):
    help = "Seed Lithuanian demo data: kids, chores from CSV, rewards from CSV"

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Existing parent username (superuser).', required=True)

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        try:
            parent = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("Parent user not found. Create superuser first.")

        # Get paths to CSV files
        data_folder = Path(__file__).parent.parent.parent.parent / 'initial_data'
        chores_file = data_folder / 'chores.csv'
        rewards_file = data_folder / 'rewards.csv'

        # Kids
        for name, theme, gender in KIDS:
            kid, created = Kid.objects.get_or_create(
                parent=parent, 
                name=name, 
                defaults={'pin': PIN, 'map_theme': theme, 'gender': gender}
            )
            if not created:
                kid.pin = PIN
                kid.active = True
                kid.map_theme = theme
                kid.gender = gender
                kid.save(update_fields=['pin', 'active', 'map_theme', 'gender'])
            self.stdout.write(self.style.SUCCESS(f"Kid ready: {kid.name} (PIN {PIN}, Theme: {theme}, Gender: {gender})"))

        # Chores from CSV
        if chores_file.exists():
            with open(chores_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    chore, created = Chore.objects.get_or_create(
                        parent=parent, 
                        title=row['title'], 
                        defaults={
                            'points': int(row['points']), 
                            'icon_emoji': row.get('icon_emoji', '✓'),
                            'active': True
                        }
                    )
                    changed = False
                    if chore.points != int(row['points']):
                        chore.points = int(row['points'])
                        changed = True
                    if not chore.icon_emoji or chore.icon_emoji != row.get('icon_emoji', '✓'):
                        chore.icon_emoji = row.get('icon_emoji', '✓')
                        changed = True
                    if changed:
                        chore.save()
                    self.stdout.write(self.style.SUCCESS(f"Chore: {row['title']} (+{row['points']}) {row.get('icon_emoji', '✓')}"))
        else:
            self.stdout.write(self.style.WARNING(f'Chores CSV not found: {chores_file}'))

        # Rewards from CSV
        if rewards_file.exists():
            with open(rewards_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    reward, created = Reward.objects.get_or_create(
                        parent=parent, 
                        title=row['title'], 
                        defaults={
                            'cost_points': int(row['cost_points']), 
                            'icon_emoji': row.get('icon_emoji', '🎁'),
                            'active': True
                        }
                    )
                    changed = False
                    if reward.cost_points != int(row['cost_points']):
                        reward.cost_points = int(row['cost_points'])
                        changed = True
                    if not reward.icon_emoji or reward.icon_emoji != row.get('icon_emoji', '🎁'):
                        reward.icon_emoji = row.get('icon_emoji', '🎁')
                        changed = True
                    if changed:
                        reward.save()
                    self.stdout.write(self.style.SUCCESS(f"Reward: {row['title']} ({row['cost_points']}) {row.get('icon_emoji', '🎁')}"))
        else:
            self.stdout.write(self.style.WARNING(f'Rewards CSV not found: {rewards_file}'))

        self.stdout.write(self.style.NOTICE("Done. Kids can log in at /kid/login/ (PIN 1234)."))
