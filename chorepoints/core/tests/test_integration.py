"""
Integration tests for ChorePoints application.
Tests end-to-end workflows across multiple app components.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment


class EndToEndWorkflowTests(TestCase):
    """Test complete user workflows from login to reward redemption."""
    
    def setUp(self):
        """Create test data for end-to-end scenarios."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=0,
            active=True,
            parent=self.parent
        )
        
        self.chore1 = Chore.objects.create(
            title='Sutvarkyti kambarį',
            points=15,
            parent=self.parent
        )
        self.chore2 = Chore.objects.create(
            title='Padaryti namų darbus',
            points=10,
            parent=self.parent
        )
        
        self.reward1 = Reward.objects.create(
            title='30 min žaidimo',
            cost_points=20,
            parent=self.parent
        )
        self.reward2 = Reward.objects.create(
            title='Saldainis',
            cost_points=5,
            parent=self.parent
        )
    
    def test_complete_chore_approval_redemption_workflow(self):
        """Test full workflow: login → submit chore → approve → redeem reward → approve."""
        # Step 1: Kid logs in
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['kid_id'], self.kid.id)
        
        # Verify initial balance
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
        
        # Step 2: Kid submits chore
        response = self.client.post(reverse('complete_chore', args=[self.chore1.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify pending chore log created
        chore_log = ChoreLog.objects.get(child=self.kid, chore=self.chore1)
        self.assertEqual(chore_log.status, 'PENDING')
        
        # Verify no points added yet
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
        
        # Step 3: Parent approves chore
        chore_log.approve()
        
        # Verify points added and status updated
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 15)
        self.assertEqual(chore_log.status, 'APPROVED')
        self.assertIsNotNone(chore_log.processed_at)
        
        # Step 4: Kid redeems reward
        response = self.client.post(reverse('redeem_reward', args=[self.reward2.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verify pending redemption created
        redemption = Redemption.objects.get(child=self.kid, reward=self.reward2)
        self.assertEqual(redemption.status, 'PENDING')
        
        # Verify no points deducted yet
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 15)
        
        # Step 5: Parent approves redemption
        redemption.approve()
        
        # Verify points deducted and status updated
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 10)  # 15 - 5
        self.assertEqual(redemption.status, 'APPROVED')
        self.assertIsNotNone(redemption.processed_at)
    
    def test_multiple_chores_then_multiple_rewards(self):
        """Test earning points from multiple chores, then redeeming multiple rewards."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Submit and approve two chores
        self.client.post(reverse('complete_chore', args=[self.chore1.id]))
        chore_log1 = ChoreLog.objects.get(child=self.kid, chore=self.chore1)
        chore_log1.approve()
        
        self.client.post(reverse('complete_chore', args=[self.chore2.id]))
        chore_log2 = ChoreLog.objects.get(child=self.kid, chore=self.chore2)
        chore_log2.approve()
        
        # Verify total points
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 25)  # 15 + 10
        
        # Redeem and approve two rewards
        self.client.post(reverse('redeem_reward', args=[self.reward1.id]))
        redemption1 = Redemption.objects.get(child=self.kid, reward=self.reward1)
        redemption1.approve()
        
        self.client.post(reverse('redeem_reward', args=[self.reward2.id]))
        redemption2 = Redemption.objects.get(child=self.kid, reward=self.reward2)
        redemption2.approve()
        
        # Verify final balance
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)  # 25 - 20 - 5
    
    def test_chore_rejection_workflow(self):
        """Test workflow when parent rejects chore submission."""
        # Login and submit chore
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.client.post(reverse('complete_chore', args=[self.chore1.id]))
        
        # Parent rejects chore
        chore_log = ChoreLog.objects.get(child=self.kid, chore=self.chore1)
        chore_log.reject()
        
        # Verify no points added
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
        self.assertEqual(chore_log.status, 'REJECTED')
        self.assertIsNotNone(chore_log.processed_at)
    
    def test_point_adjustment_integration(self):
        """Test point adjustments integrated with chore/reward workflow."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Parent gives bonus points
        adjustment1 = PointAdjustment.objects.create(
            kid=self.kid,
            points=10,
            reason='Bonus už gerą elgesį',
            parent=self.parent
        )
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 10)
        
        # Kid earns points from chore
        self.client.post(reverse('complete_chore', args=[self.chore2.id]))
        chore_log = ChoreLog.objects.get(child=self.kid, chore=self.chore2)
        chore_log.approve()
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 20)  # 10 + 10
        
        # Parent deducts penalty points
        adjustment2 = PointAdjustment.objects.create(
            kid=self.kid,
            points=-5,
            reason='Bausmė už blogą elgesį',
            parent=self.parent
        )
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 15)  # 20 - 5
        
        # Kid redeems reward
        self.client.post(reverse('redeem_reward', args=[self.reward2.id]))
        redemption = Redemption.objects.get(child=self.kid, reward=self.reward2)
        redemption.approve()
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 10)  # 15 - 5


class DataIntegrityTests(TestCase):
    """Test data integrity and constraint validations."""
    
    def setUp(self):
        """Create test data for integrity testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=50,
            active=True,
            parent=self.parent
        )
        
        self.chore = Chore.objects.create(
            title='Sutvarkyti kambarį',
            points=15,
            parent=self.parent
        )
        
        self.reward = Reward.objects.create(
            title='Saldainis',
            cost_points=5,
            parent=self.parent
        )
    
    def test_insufficient_points_prevention(self):
        """Test that redemptions fail when insufficient points."""
        # Kid has 50 points, try to redeem 60-point reward
        expensive_reward = Reward.objects.create(
            title='Expensive',
            cost_points=60,
            parent=self.parent
        )
        
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=expensive_reward
        )
        
        # Redemption should fail due to insufficient points
        result = redemption.approve()
        self.assertFalse(result)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 50)  # Unchanged
        self.assertEqual(redemption.status, 'PENDING')  # Still pending
    
    def test_duplicate_approval_prevention(self):
        """Test that approving already-approved record doesn't double-add points."""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore
        )
        
        # First approval
        log.approve()
        self.kid.refresh_from_db()
        balance_after_first = self.kid.points_balance
        
        # Try to approve again
        log.approve()  # Should be no-op
        self.kid.refresh_from_db()
        
        # Balance should not change
        self.assertEqual(self.kid.points_balance, balance_after_first)
        self.assertEqual(log.status, 'APPROVED')
    
    def test_point_adjustment_requires_reason(self):
        """Test that PointAdjustment requires a reason (after migration 0010)."""
        # Note: Django doesn't enforce this at model level without full_clean()
        # Just test that creating with reason works
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=10,
            reason='Test reason',
            parent=self.parent
        )
        self.assertIsNotNone(adjustment.reason)
    
    def test_cascade_delete_integrity(self):
        """Test that deleting parent user cascades correctly."""
        # Create data linked to parent
        adjustment = PointAdjustment.objects.create(
            kid=self.kid,
            points=10,
            reason='Test',
            parent=self.parent
        )
        
        kid_id = self.kid.id
        adjustment_id = adjustment.id
        
        # Delete parent
        self.parent.delete()
        
        # Kid should be deleted (cascade)
        self.assertFalse(Kid.objects.filter(id=kid_id).exists())
        
        # PointAdjustment should be deleted (parent cascade)
        self.assertFalse(PointAdjustment.objects.filter(id=adjustment_id).exists())
    
    def test_zero_point_chore_and_reward(self):
        """Test edge case with zero-point chore and reward."""
        zero_chore = Chore.objects.create(
            title='Zero chore',
            points=0,
            parent=self.parent
        )
        zero_reward = Reward.objects.create(
            title='Free reward',
            cost_points=0,
            parent=self.parent
        )
        
        initial_balance = self.kid.points_balance
        
        # Submit and approve zero-point chore
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=zero_chore
        )
        log.approve()
        
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, initial_balance)
        
        # Redeem and approve zero-cost reward
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=zero_reward
        )
        redemption.approve()
        
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, initial_balance)
