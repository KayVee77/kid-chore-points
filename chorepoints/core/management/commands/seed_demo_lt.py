from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.models import Kid, Chore, Reward

KIDS = [
    ("Elija", "ISLAND", "F"),  # Girl
    ("Agota", "SPACE", "F"),   # Girl
]
PIN = "1234"
CHORES = [
    ("Išnešti šiukšles", 2, "🗑️"),
    ("Susitvarkyti kambarį", 3, "🧸"),
    ("Išplauti indus", 2, "🍽️"),
    ("Pamaitinti augintinį", 1, "🐾"),
]
REWARDS = [
    ("30 min ekranui", 5, "🕹️"),
    ("Saldi užkandėlė", 4, "🍬"),
    ("Vakaras be namų ruošos", 8, "🌙"),
]

class Command(BaseCommand):
    help = "Seed Lithuanian demo data: kids, chores, rewards"

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Existing parent username (superuser).', required=True)

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        try:
            parent = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError("Parent user not found. Create superuser first.")

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

        # Chores
        for title, points, emoji in CHORES:
            chore, created = Chore.objects.get_or_create(parent=parent, title=title, defaults={'points': points, 'icon_emoji': emoji})
            changed = False
            if chore.points != points:
                chore.points = points
                changed = True
            if not chore.icon_emoji:
                chore.icon_emoji = emoji
                changed = True
            if changed:
                chore.save()
            self.stdout.write(self.style.SUCCESS(f"Chore: {title} (+{points}) {emoji}"))

        # Rewards
        for title, cost, emoji in REWARDS:
            reward, created = Reward.objects.get_or_create(parent=parent, title=title, defaults={'cost_points': cost, 'icon_emoji': emoji})
            changed = False
            if reward.cost_points != cost:
                reward.cost_points = cost
                changed = True
            if not reward.icon_emoji:
                reward.icon_emoji = emoji
                changed = True
            if changed:
                reward.save()
            self.stdout.write(self.style.SUCCESS(f"Reward: {title} ({cost}) {emoji}"))

        self.stdout.write(self.style.NOTICE("Done. Kids can log in at /kid/login/ (PIN 1234)."))
