from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.models import Kid, Chore, Reward

KIDS = ["Elija", "Agota"]
PIN = "1234"
CHORES = [
    ("Išnešti šiukšles", 2),
    ("Susitvarkyti kambarį", 3),
    ("Išplauti indus", 2),
    ("Pamaitinti augintinį", 1),
]
REWARDS = [
    ("30 min ekranui", 5),
    ("Saldi užkandėlė", 4),
    ("Vakaras be namų ruošos", 8),
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
        for name in KIDS:
            kid, created = Kid.objects.get_or_create(parent=parent, name=name, defaults={'pin': PIN})
            if not created:
                kid.pin = PIN
                kid.active = True
                kid.save(update_fields=['pin','active'])
            self.stdout.write(self.style.SUCCESS(f"Kid ready: {kid.name} (PIN {PIN})"))

        # Chores
        for title, points in CHORES:
            chore, created = Chore.objects.get_or_create(parent=parent, title=title, defaults={'points': points})
            if not created and chore.points != points:
                chore.points = points
                chore.save(update_fields=['points'])
            self.stdout.write(self.style.SUCCESS(f"Chore: {title} (+{points})"))

        # Rewards
        for title, cost in REWARDS:
            reward, created = Reward.objects.get_or_create(parent=parent, title=title, defaults={'cost_points': cost})
            if not created and reward.cost_points != cost:
                reward.cost_points = cost
                reward.save(update_fields=['cost_points'])
            self.stdout.write(self.style.SUCCESS(f"Reward: {title} ({cost})"))

        self.stdout.write(self.style.NOTICE("Done. Kids can log in at /kid/login/ (PIN 1234)."))
