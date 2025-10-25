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

class Kid(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kids")
    name = models.CharField(max_length=100)
    pin = models.CharField(max_length=20)  # Plaintext (MVP only)
    points_balance = models.IntegerField(default=0)
    map_position = models.IntegerField(default=0, help_text="Nuotykių žemėlapio pozicija (suskaičiuoti taškai)")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_emoji = models.CharField(max_length=4, blank=True, default="", help_text="Emoji (jei tuščia – generuojama raidė)")
    photo = models.ImageField(upload_to="kid_avatars/", null=True, blank=True, help_text="Nuotrauka (jei nenaudojamas emoji)")

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

    def get_map_progress(self) -> dict:
        """Calculate adventure map progress based on reward costs."""
        from .models import Reward  # Avoid circular import
        
        # Get all active rewards ordered by cost_points (milestones)
        rewards = Reward.objects.filter(parent=self.parent, active=True).order_by('cost_points')
        
        milestones = []
        for reward in rewards:
            milestones.append({
                'position': reward.cost_points,
                'reward_id': reward.id,
                'reward_title': reward.title,
                'reward_icon': reward.display_icon,
            })
        
        # Find next reward position
        next_reward_position = None
        next_reward = None
        for milestone in milestones:
            if milestone['position'] > self.map_position:
                next_reward_position = milestone['position']
                next_reward = milestone
                break
        
        # Calculate progress percentage to next reward
        progress_percentage = 0
        if next_reward_position:
            # Find previous milestone (or 0 if this is the first)
            prev_position = 0
            for milestone in milestones:
                if milestone['position'] < next_reward_position:
                    prev_position = milestone['position']
            
            segment_length = next_reward_position - prev_position
            progress_in_segment = self.map_position - prev_position
            
            if segment_length > 0:
                progress_percentage = min(100, int((progress_in_segment / segment_length) * 100))
        
        # Calculate points needed to next reward
        points_needed = next_reward_position - self.map_position if next_reward_position else 0
        
        return {
            'current_position': self.map_position,
            'milestones': milestones,
            'next_reward_position': next_reward_position,
            'next_reward': next_reward,
            'progress_percentage': progress_percentage,
            'points_needed': points_needed,
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
            self.child.points_balance += self.points_awarded
            self.child.map_position += self.points_awarded
            self.child.save(update_fields=["points_balance", "map_position"])
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
        # ensure sufficient points at approval time
        if self.child.points_balance < self.cost_points:
            return False
        with transaction.atomic():
            self.child.points_balance -= self.cost_points
            self.child.save(update_fields=["points_balance"])
            self.status = self.Status.APPROVED
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
            self.kid.points_balance += self.points
            self.kid.save(update_fields=["points_balance"])

    def __str__(self):
        sign = '+' if self.points >= 0 else ''
        return f"Adj {sign}{self.points} for {self.kid.name}"

    def reject(self):
        if self.status != self.Status.PENDING:
            return False
        self.status = self.Status.REJECTED
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        return True
