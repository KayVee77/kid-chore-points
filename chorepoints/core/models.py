from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from pathlib import Path
from io import BytesIO
try:
    from PIL import Image
except ImportError:  # Pillow should be installed; safeguard
    Image = None

User = get_user_model()

# Achievement Milestones Configuration (Infinite Progressive System)
ACHIEVEMENT_MILESTONES = [
    {'position': 50, 'name': 'Bronzos ženkliukas', 'icon': '🥉', 'bonus': 10},
    {'position': 100, 'name': 'Sidabro ženkliukas', 'icon': '🥈', 'bonus': 10},
    {'position': 200, 'name': 'Aukso ženkliukas', 'icon': '🥇', 'bonus': 15},
    {'position': 300, 'name': 'Deimanto ženkliukas', 'icon': '💎', 'bonus': 15},
    {'position': 500, 'name': 'Karūnos ženkliukas', 'icon': '👑', 'bonus': 20},
    {'position': 750, 'name': 'Žvaigždės ženkliukas', 'icon': '⭐', 'bonus': 20},
    {'position': 1000, 'name': 'Superžvaigždė', 'icon': '🌟', 'bonus': 25},
    {'position': 1500, 'name': 'Čempionas', 'icon': '🏆', 'bonus': 30},
    {'position': 2000, 'name': 'Legenda', 'icon': '🔥', 'bonus': 40},
    {'position': 3000, 'name': 'Herojus', 'icon': '🚀', 'bonus': 50},
]

class Kid(models.Model):
    class MapTheme(models.TextChoices):
        ISLAND = "ISLAND", "Island"
        SPACE = "SPACE", "Space"
        RAINBOW = "RAINBOW", "Rainbow Road"
    
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kids")
    name = models.CharField(max_length=100)
    pin = models.CharField(max_length=20)  # Plaintext (MVP only)
    points_balance = models.IntegerField(default=0)
    map_position = models.IntegerField(default=0, help_text="Nuotykių žemėlapio pozicija (suskaičiuoti taškai)")
    highest_milestone = models.IntegerField(default=0, help_text="Aukščiausias pasiektas milestone pozicija")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_emoji = models.CharField(max_length=4, blank=True, default="", help_text="Emoji (jei tuščia – generuojama raidė)")
    photo = models.ImageField(upload_to="kid_avatars/", null=True, blank=True, help_text="Nuotrauka (jei nenaudojamas emoji)")
    map_theme = models.CharField(max_length=10, choices=MapTheme.choices, default=MapTheme.ISLAND, help_text="Nuotykių žemėlapio tema")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After initial save ensure photo (if any) is resized (max 400x400)
        if self.photo and Image:
            photo_path = Path(self.photo.path)
            try:
                with Image.open(photo_path) as img:
                    if img.width > 400 or img.height > 400:
                        img.thumbnail((400, 400))
                        img.save(photo_path)
            except Exception:
                # silently ignore processing errors (keep original)
                pass

    @property
    def display_letter(self) -> str:
        if self.name:
            return self.name[0].upper()
        return "?"

    def get_current_milestone(self) -> dict:
        """Get the highest milestone achieved by this kid."""
        achieved = None
        for milestone in ACHIEVEMENT_MILESTONES:
            if self.map_position >= milestone['position']:
                achieved = milestone
            else:
                break
        return achieved

    def get_next_milestone(self) -> dict:
        """Get the next milestone to achieve."""
        for milestone in ACHIEVEMENT_MILESTONES:
            if milestone['position'] > self.map_position:
                return milestone
        # If beyond all defined milestones, continue with bonus intervals
        if self.map_position >= ACHIEVEMENT_MILESTONES[-1]['position']:
            # After last milestone, give bonuses every 500 points
            next_interval = ((self.map_position // 500) + 1) * 500
            return {
                'position': next_interval,
                'name': 'Bonus',
                'icon': '🎁',
                'bonus': 50
            }
        return None

    def get_map_progress(self) -> dict:
        """Calculate adventure map progress based on achievement milestones."""
        current_milestone = self.get_current_milestone()
        next_milestone = self.get_next_milestone()
        
        # Calculate progress to next milestone
        progress_percentage = 0
        points_needed = 0
        
        if next_milestone:
            prev_position = current_milestone['position'] if current_milestone else 0
            segment_length = next_milestone['position'] - prev_position
            progress_in_segment = self.map_position - prev_position
            
            if segment_length > 0:
                progress_percentage = min(100, int((progress_in_segment / segment_length) * 100))
            
            points_needed = next_milestone['position'] - self.map_position
        
        # Build milestone display list
        milestones = []
        for milestone in ACHIEVEMENT_MILESTONES:
            status = 'achieved' if self.map_position >= milestone['position'] else 'locked'
            aria_status = 'pasiekta' if status == 'achieved' else f"dar reikia {milestone['position'] - self.map_position} taškų"
            
            milestones.append({
                'position': milestone['position'],
                'name': milestone['name'],
                'icon': milestone['icon'],
                'bonus': milestone['bonus'],
                'status': status,
                'aria_label': f"{milestone['name']}, {milestone['position']} taškai, {aria_status}",
            })
        
        return {
            'current_position': self.map_position,
            'current_milestone': current_milestone,
            'next_milestone': next_milestone,
            'milestones': milestones,
            'progress_percentage': progress_percentage,
            'points_needed': points_needed,
            'total_points_earned': self.map_position,
        }

    def __str__(self):
        return f"{self.name} ({self.parent.username})"

class Chore(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chores")
    title = models.CharField(max_length=200)
    points = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    icon_emoji = models.CharField(max_length=8, blank=True, default="", help_text="Emoji (pvz. 🧹) – jei nėra paveikslėlio")
    icon_image = models.ImageField(upload_to="chore_icons/", null=True, blank=True, help_text="Paveikslėlis (128x128 rekomenduojama)")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.icon_image and Image:
            from PIL import Image as PilImage
            path = Path(self.icon_image.path)
            try:
                with PilImage.open(path) as img:
                    if img.width > 128 or img.height > 128:
                        img.thumbnail((128,128))
                        img.save(path)
            except Exception:
                pass

    @property
    def display_icon(self):
        return self.icon_emoji or "🧹"

    def __str__(self):
        return f"{self.title} (+{self.points} pts)"

class Reward(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rewards")
    title = models.CharField(max_length=200)
    cost_points = models.IntegerField(default=5)
    active = models.BooleanField(default=True)
    icon_emoji = models.CharField(max_length=8, blank=True, default="", help_text="Emoji (pvz. 🎁) – jei nėra paveikslėlio")
    icon_image = models.ImageField(upload_to="reward_icons/", null=True, blank=True, help_text="Paveikslėlis (128x128 rekomenduojama)")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.icon_image and Image:
            from PIL import Image as PilImage
            path = Path(self.icon_image.path)
            try:
                with PilImage.open(path) as img:
                    if img.width > 128 or img.height > 128:
                        img.thumbnail((128,128))
                        img.save(path)
            except Exception:
                pass

    @property
    def display_icon(self):
        return self.icon_emoji or "🎁"

    def __str__(self):
        return f"{self.title} (-{self.cost_points} pts)"

class ChoreLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    child = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="chore_logs")
    chore = models.ForeignKey(Chore, on_delete=models.PROTECT)
    logged_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    processed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding and not self.points_awarded:
            self.points_awarded = self.chore.points
        super().save(*args, **kwargs)

    def approve(self):
        if self.status != self.Status.PENDING:
            return False
        with transaction.atomic():
            # Refresh child from DB to avoid race conditions when approving multiple logs
            self.child.refresh_from_db()
            old_position = self.child.map_position
            self.child.points_balance += self.points_awarded
            self.child.map_position += self.points_awarded
            
            # Check if any milestones were crossed and award bonuses
            milestones_crossed = []
            for milestone in ACHIEVEMENT_MILESTONES:
                if old_position < milestone['position'] <= self.child.map_position:
                    milestones_crossed.append(milestone)
            
            # Check for bonuses after the last defined milestone (every 500 pts)
            last_milestone_position = ACHIEVEMENT_MILESTONES[-1]['position']
            if old_position >= last_milestone_position:
                # Check every 500-point interval crossed
                old_interval = old_position // 500
                new_interval = self.child.map_position // 500
                intervals_crossed = new_interval - old_interval
                
                if intervals_crossed > 0:
                    for _ in range(intervals_crossed):
                        milestones_crossed.append({
                            'position': (old_interval + 1) * 500,
                            'name': 'Bonus Milestone',
                            'icon': '🎁',
                            'bonus': 50
                        })
            
            # Award bonuses for crossed milestones
            for milestone in milestones_crossed:
                self.child.points_balance += milestone['bonus']
                self.child.map_position += milestone['bonus']
                if milestone['position'] <= last_milestone_position:
                    self.child.highest_milestone = milestone['position']
            
            self.child.save(update_fields=["points_balance", "map_position", "highest_milestone"])
            self.status = self.Status.APPROVED
            self.processed_at = timezone.now()
            self.save(update_fields=["status", "processed_at"])
        return True

    def reject(self):
        if self.status != self.Status.PENDING:
            return False
        self.status = self.Status.REJECTED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        return True

class Redemption(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    child = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="redemptions")
    reward = models.ForeignKey(Reward, on_delete=models.PROTECT)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    cost_points = models.IntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    processed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding and not self.cost_points:
            self.cost_points = self.reward.cost_points
        super().save(*args, **kwargs)

    def approve(self):
        if self.status != self.Status.PENDING:
            return False
        with transaction.atomic():
            # Refresh child from DB to avoid race conditions when approving multiple redemptions
            self.child.refresh_from_db()
            # ensure sufficient points at approval time
            if self.child.points_balance < self.cost_points:
                return False
            self.child.points_balance -= self.cost_points
            self.child.save(update_fields=["points_balance"])
            self.status = self.Status.APPROVED
            self.processed_at = timezone.now()
            self.save(update_fields=["status", "processed_at"])
        return True

    def reject(self):
        if self.status != self.Status.PENDING:
            return False
        self.status = self.Status.REJECTED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        return True


class PointAdjustment(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="point_adjustments")
    kid = models.ForeignKey(Kid, on_delete=models.CASCADE, related_name="point_adjustments")
    points = models.IntegerField(help_text="Positive or negative integer to adjust balance")
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            # apply adjustment after creation to have record even if update fails
            old_position = self.kid.map_position
            self.kid.points_balance += self.points
            # Also update map_position for positive adjustments
            if self.points > 0:
                self.kid.map_position += self.points
                
                # Check if any milestones were crossed and award bonuses
                milestones_crossed = []
                for milestone in ACHIEVEMENT_MILESTONES:
                    if old_position < milestone['position'] <= self.kid.map_position:
                        milestones_crossed.append(milestone)
                
                # Check for bonuses after the last defined milestone (every 500 pts)
                last_milestone_position = ACHIEVEMENT_MILESTONES[-1]['position']
                if old_position >= last_milestone_position:
                    # Check every 500-point interval crossed
                    old_interval = old_position // 500
                    new_interval = self.kid.map_position // 500
                    intervals_crossed = new_interval - old_interval
                    
                    if intervals_crossed > 0:
                        for _ in range(intervals_crossed):
                            milestones_crossed.append({
                                'position': (old_interval + 1) * 500,
                                'name': 'Bonus Milestone',
                                'icon': '🎁',
                                'bonus': 50
                            })
                
                # Award bonuses for crossed milestones
                for milestone in milestones_crossed:
                    self.kid.points_balance += milestone['bonus']
                    self.kid.map_position += milestone['bonus']
                    if milestone['position'] <= last_milestone_position:
                        self.kid.highest_milestone = milestone['position']
            
            self.kid.save(update_fields=["points_balance", "map_position", "highest_milestone"])

    def __str__(self):
        sign = '+' if self.points >= 0 else ''
        return f"Adj {sign}{self.points} for {self.kid.name}"
