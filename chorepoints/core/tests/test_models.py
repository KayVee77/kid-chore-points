"""
Unit tests for core models.

Tests cover:
- Kid model: creation, PIN validation, points balance operations
- Chore/Reward models: creation, validation
- ChoreLog model: creation, approval/rejection, points updates
- Redemption model: creation, approval/rejection, points deduction
- PointAdjustment model: creation, automatic balance updates
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import transaction
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment


class KidModelTests(TestCase):
    """Test Kid model functionality."""
    
    def setUp(self):
        """Set up test user and kid."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=0
        )
    
    def test_kid_creation(self):
        """Test kid can be created with required fields."""
        self.assertEqual(self.kid.name, 'TestKid')
        self.assertEqual(self.kid.pin, '1234')
        self.assertEqual(self.kid.points_balance, 0)
        self.assertTrue(self.kid.active)
    
    def test_kid_string_representation(self):
        """Test kid __str__ method."""
        expected = f"{self.kid.name} ({self.user.username})"
        self.assertEqual(str(self.kid), expected)
    
    def test_kid_points_balance_default(self):
        """Test kid starts with 0 points by default."""
        new_kid = Kid.objects.create(
            name='NewKid',
            parent=self.user,
            pin='5678'
        )
        self.assertEqual(new_kid.points_balance, 0)
    
    def test_kid_pin_storage(self):
        """Test PIN is stored as plaintext (MVP limitation)."""
        self.assertEqual(self.kid.pin, '1234')
        # Note: In production, this should be hashed


class ChoreModelTests(TestCase):
    """Test Chore model functionality."""
    
    def setUp(self):
        """Set up test user and chore."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.chore = Chore.objects.create(
            title='Test Chore',
            points=10,
            parent=self.user,
            icon_emoji='🧹'
        )
    
    def test_chore_creation(self):
        """Test chore can be created."""
        self.assertEqual(self.chore.title, 'Test Chore')
        self.assertEqual(self.chore.points, 10)
        self.assertEqual(self.chore.icon_emoji, '🧹')
    
    def test_chore_string_representation(self):
        """Test chore __str__ method."""
        expected = f"Test Chore (+{self.chore.points} pts)"
        self.assertEqual(str(self.chore), expected)


class RewardModelTests(TestCase):
    """Test Reward model functionality."""
    
    def setUp(self):
        """Set up test user and reward."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.reward = Reward.objects.create(
            title='Test Reward',
            cost_points=20,
            parent=self.user,
            icon_emoji='🎁'
        )
    
    def test_reward_creation(self):
        """Test reward can be created."""
        self.assertEqual(self.reward.title, 'Test Reward')
        self.assertEqual(self.reward.cost_points, 20)
        self.assertEqual(self.reward.icon_emoji, '🎁')
    
    def test_reward_string_representation(self):
        """Test reward __str__ method."""
        expected = f"Test Reward (-{self.reward.cost_points} pts)"
        self.assertEqual(str(self.reward), expected)


class ChoreLogModelTests(TestCase):
    """Test ChoreLog model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=0
        )
        self.chore = Chore.objects.create(
            title='Clean Room',
            points=15,
            parent=self.user
        )
    
    def test_chorelog_creation_pending(self):
        """Test ChoreLog is created with PENDING status."""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=self.chore.points
        )
        self.assertEqual(log.status, 'PENDING')
        self.assertIsNone(log.processed_at)
    
    def test_chorelog_approve_adds_points(self):
        """Test approving ChoreLog adds points to kid."""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=15
        )
        
        log.approve()
        
        self.assertEqual(log.status, 'APPROVED')
        self.assertIsNotNone(log.processed_at)
        
        # Refresh kid from DB and check points
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 15)
    
    def test_chorelog_reject_no_points(self):
        """Test rejecting ChoreLog does not add points."""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=15
        )
        
        log.reject()
        
        self.assertEqual(log.status, 'REJECTED')
        self.assertIsNotNone(log.processed_at)
        
        # Check points remain 0
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
    
    def test_chorelog_bulk_approve_race_condition_fix(self):
        """Test bulk approval uses refresh_from_db() to prevent race condition."""
        # Create 3 ChoreLog entries
        log1 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=15)
        log2 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=5)
        log3 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        
        # Approve all three (simulating bulk admin action)
        log1.approve()
        log2.approve()
        log3.approve()
        
        # Check final points (should be 15+5+10=30, not just 10)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 30)
    
    def test_chorelog_string_representation(self):
        """Test ChoreLog __str__ method."""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=15
        )
        # ChoreLog uses default Django __str__
        expected = f"ChoreLog object ({log.id})"
        self.assertEqual(str(log), expected)


class RedemptionModelTests(TestCase):
    """Test Redemption model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=50
        )
        self.reward = Reward.objects.create(
            title='Ice Cream',
            cost_points=20,
            parent=self.user
        )
    
    def test_redemption_creation_pending(self):
        """Test Redemption is created with PENDING status."""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=self.reward.cost_points
        )
        self.assertEqual(redemption.status, 'PENDING')
        self.assertIsNone(redemption.processed_at)
    
    def test_redemption_approve_deducts_points(self):
        """Test approving Redemption deducts points from kid."""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=20
        )
        
        redemption.approve()
        
        self.assertEqual(redemption.status, 'APPROVED')
        self.assertIsNotNone(redemption.processed_at)
        
        # Check points deducted (50 - 20 = 30)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 30)
    
    def test_redemption_reject_no_deduction(self):
        """Test rejecting Redemption does not deduct points."""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=20
        )
        
        redemption.reject()
        
        self.assertEqual(redemption.status, 'REJECTED')
        self.assertIsNotNone(redemption.processed_at)
        
        # Check points remain unchanged
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 50)
    
    def test_redemption_string_representation(self):
        """Test Redemption __str__ method."""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=20
        )
        # Redemption uses default Django __str__
        expected = f"Redemption object ({redemption.id})"
        self.assertEqual(str(redemption), expected)


class PointAdjustmentModelTests(TestCase):
    """Test PointAdjustment model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=10
        )
    
    def test_point_adjustment_positive(self):
        """Test positive point adjustment adds points."""
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=5,
            reason='Good behavior bonus',
            parent=self.user
        )
        
        # Check points added (10 + 5 = 15)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 15)
    
    def test_point_adjustment_negative(self):
        """Test negative point adjustment subtracts points."""
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=-3,
            reason='Penalty',
            parent=self.user
        )
        
        # Check points subtracted (10 - 3 = 7)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 7)
    
    def test_point_adjustment_string_representation(self):
        """Test PointAdjustment __str__ method."""
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=5,
            reason='Bonus',
            parent=self.user
        )
        expected = f"Adj +{adjustment.points} for {self.kid.name}"
        self.assertEqual(str(adjustment), expected)
    
    def test_point_adjustment_negative_string(self):
        """Test PointAdjustment __str__ for negative adjustment."""
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=-3,
            reason='Penalty',
            parent=self.user
        )
        # Should show -3, not +-3
        expected = f"Adj -3 for {self.kid.name}"
        self.assertEqual(str(adjustment), expected)


class ModelIntegrationTests(TestCase):
    """Test integration between models."""
    
    def setUp(self):
        """Set up comprehensive test scenario."""
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=0
        )
        self.chore = Chore.objects.create(
            title='Test Chore',
            points=10,
            parent=self.user
        )
        self.reward = Reward.objects.create(
            title='Test Reward',
            cost_points=25,
            parent=self.user
        )
    
    def test_full_workflow_chore_to_reward(self):
        """Test complete workflow: submit chores, approve, redeem reward."""
        # Step 1: Submit 3 chores
        log1 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        log2 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        log3 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        
        # Step 2: Approve all chores (bulk)
        log1.approve()
        log2.approve()
        log3.approve()
        
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 30)
        
        # Step 3: Redeem reward
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=25
        )
        redemption.approve()
        
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 5)  # 30 - 25 = 5
    
    def test_point_adjustment_with_existing_balance(self):
        """Test point adjustments work correctly with existing balance."""
        # Give kid some points via chore
        log = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        log.approve()
        
        # Add bonus points
        PointAdjustment.objects.create(
            kid=self.kid,
            points=8,
            reason='QA bonus',
            parent=self.user
        )
        
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 18)  # 10 + 8
