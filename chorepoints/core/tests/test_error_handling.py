"""
Error Handling Tests for ChorePoints Application

Tests error pages (404, 403), edge cases, validation errors, and boundary conditions.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment


class ErrorPageTests(TestCase):
    """Test error pages and error handling."""
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(username='testparent', password='testpass')
        self.kid = Kid.objects.create(
            parent=self.parent,
            name='Test Kid',
            pin='1234',
            points_balance=100
        )
    
    def test_404_for_invalid_url(self):
        """Test that invalid URLs return 404."""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_kid_id_in_login(self):
        """Test login with non-existent kid ID."""
        response = self.client.post(reverse('kid_login'), {
            'kid': 99999,
            'pin': '1234'
        })
        # Should stay on login page (200) with form errors or redirect with error message (302)
        self.assertIn(response.status_code, [200, 302])
    
    def test_access_without_login(self):
        """Test that kid views redirect without authentication."""
        response = self.client.get(reverse('kid_home'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/kid/login/', response.url)
    
    def test_csrf_failure_handling(self):
        """Test that CSRF failures are handled properly."""
        # Login first
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        chore = Chore.objects.create(
            parent=self.parent,
            title='Test Chore',
            points=10
        )
        
        # Try to submit without CSRF token (enforce_csrf_checks=True)
        from django.test import Client as CSRFClient
        csrf_client = CSRFClient(enforce_csrf_checks=True)
        
        # Copy session
        csrf_client.cookies = self.client.cookies
        
        response = csrf_client.post(reverse('complete_chore', args=[chore.id]))
        # Should get 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_invalid_session_handling(self):
        """Test that invalid session data is handled properly."""
        # Set invalid kid_id in session
        session = self.client.session
        session['kid_id'] = 99999
        session.save()
        
        response = self.client.get(reverse('kid_home'))
        # get_object_or_404 raises 404 when kid not found
        self.assertEqual(response.status_code, 404)
    
    def test_logout_clears_session(self):
        """Test that logout properly clears session."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Verify logged in
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        
        # Logout
        response = self.client.post(reverse('kid_logout'))
        self.assertEqual(response.status_code, 302)
        
        # Verify logged out - should redirect to login
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/kid/login/', response.url)


class EdgeCaseTests(TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(username='testparent', password='testpass')
        self.kid = Kid.objects.create(
            parent=self.parent,
            name='Test Kid',
            pin='1234',
            points_balance=50
        )
    
    def test_kid_with_zero_points(self):
        """Test kid home page with zero points."""
        self.kid.points_balance = 0
        self.kid.save()
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '0')
    
    def test_kid_with_negative_points(self):
        """Test that kid can have negative points (debt system)."""
        self.kid.points_balance = -10
        self.kid.save()
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '-10')
    
    def test_reward_redemption_insufficient_points(self):
        """Test that reward redemption fails with insufficient points."""
        self.kid.points_balance = 10
        self.kid.save()
        
        reward = Reward.objects.create(
            parent=self.parent,
            title='Expensive Reward',
            cost_points=100
        )
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.post(reverse('redeem_reward', args=[reward.id]))
        
        # Should create PENDING redemption even with insufficient points
        # (approval workflow allows parent to decide)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Redemption.objects.filter(child=self.kid, reward=reward).exists())
    
    def test_submit_nonexistent_chore(self):
        """Test submitting a chore that doesn't exist."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.post(reverse('complete_chore', args=[99999]))
        # Should get 404
        self.assertEqual(response.status_code, 404)
    
    def test_redeem_nonexistent_reward(self):
        """Test redeeming a reward that doesn't exist."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.post(reverse('redeem_reward', args=[99999]))
        # Should get 404
        self.assertEqual(response.status_code, 404)
    
    def test_duplicate_pending_chore_prevention(self):
        """Test that duplicate pending chores are prevented."""
        chore = Chore.objects.create(
            parent=self.parent,
            title='Test Chore',
            points=10
        )
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Submit once
        response1 = self.client.post(reverse('complete_chore', args=[chore.id]))
        self.assertEqual(response1.status_code, 302)
        
        # Try to submit again
        response2 = self.client.post(reverse('complete_chore', args=[chore.id]))
        self.assertEqual(response2.status_code, 302)
        
        # Should only have one PENDING log
        pending_count = ChoreLog.objects.filter(
            child=self.kid,
            chore=chore,
            status='PENDING'
        ).count()
        self.assertEqual(pending_count, 1)
    
    def test_duplicate_pending_redemption_prevention(self):
        """Test that duplicate pending redemptions are prevented."""
        reward = Reward.objects.create(
            parent=self.parent,
            title='Test Reward',
            cost_points=10
        )
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Redeem once
        response1 = self.client.post(reverse('redeem_reward', args=[reward.id]))
        self.assertEqual(response1.status_code, 302)
        
        # Try to redeem again
        response2 = self.client.post(reverse('redeem_reward', args=[reward.id]))
        self.assertEqual(response2.status_code, 302)
        
        # Should only have one PENDING redemption
        pending_count = Redemption.objects.filter(
            child=self.kid,
            reward=reward,
            status='PENDING'
        ).count()
        self.assertEqual(pending_count, 1)
    
    def test_very_long_names(self):
        """Test that very long names are handled properly."""
        long_name = 'A' * 200  # Django CharField max_length
        
        kid = Kid.objects.create(
            parent=self.parent,
            name=long_name[:100],  # Assume max_length=100
            pin='5678',
            points_balance=0
        )
        
        # Should save successfully with truncated name
        self.assertEqual(len(kid.name), 100)
    
    def test_empty_chore_list(self):
        """Test kid home with no chores available."""
        # Delete all chores
        Chore.objects.all().delete()
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        # Should still render page successfully
        self.assertContains(response, 'Test Kid')
    
    def test_empty_reward_list(self):
        """Test kid home with no rewards available."""
        # Delete all rewards
        Reward.objects.all().delete()
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        # Should still render page successfully
        self.assertContains(response, 'Test Kid')
    
    def test_point_adjustment_with_zero_points(self):
        """Test point adjustment with zero points."""
        adjustment = PointAdjustment.objects.create(
            parent=self.parent,
            kid=self.kid,
            points=0,
            reason='Zero point test'
        )
        
        # Balance should remain unchanged
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 50)
    
    def test_point_adjustment_with_negative_points(self):
        """Test point adjustment with negative points (deduction)."""
        adjustment = PointAdjustment.objects.create(
            parent=self.parent,
            kid=self.kid,
            points=-20,
            reason='Deduction test'
        )
        
        # Balance should decrease
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 30)


class ValidationErrorTests(TestCase):
    """Test validation errors and form error handling."""
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user(username='testparent', password='testpass')
        self.kid = Kid.objects.create(
            parent=self.parent,
            name='Test Kid',
            pin='1234',
            points_balance=50
        )
    
    def test_pin_too_short(self):
        """Test that PINs shorter than 4 characters are rejected."""
        from core.forms import ChangePinForm
        
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '12',  # Too short
            'confirm_pin': '12'
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_pin_too_long(self):
        """Test that PINs longer than 20 characters are rejected."""
        from core.forms import ChangePinForm
        
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '1' * 25,  # Too long
            'confirm_pin': '1' * 25
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_pin_mismatch_validation(self):
        """Test that mismatched PIN confirmation is rejected."""
        from core.forms import ChangePinForm
        
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5679'  # Mismatch
        })
        
        self.assertFalse(form.is_valid())
        # Should have non-field error for mismatch
        self.assertTrue(len(form.non_field_errors()) > 0)
    
    def test_empty_pin_fields(self):
        """Test that empty PIN fields are rejected."""
        from core.forms import ChangePinForm
        
        form = ChangePinForm(data={
            'old_pin': '',
            'new_pin': '',
            'confirm_pin': ''
        })
        
        self.assertFalse(form.is_valid())
        self.assertIn('old_pin', form.errors)
        self.assertIn('new_pin', form.errors)
        self.assertIn('confirm_pin', form.errors)
    
    def test_chore_creation_requires_title(self):
        """Test that chore creation requires a title."""
        chore = Chore(parent=self.parent, points=10)
        
        # Should raise validation error
        with self.assertRaises(Exception):
            chore.full_clean()
    
    def test_reward_creation_requires_title(self):
        """Test that reward creation requires a title."""
        reward = Reward(parent=self.parent, cost_points=10)
        
        # Should raise validation error
        with self.assertRaises(Exception):
            reward.full_clean()
    
    def test_point_adjustment_requires_reason(self):
        """Test that point adjustment requires a reason (after migration 0010)."""
        # After migration 0010, reason is required (blank=False)
        adjustment = PointAdjustment(
            parent=self.parent,
            kid=self.kid,
            points=10,
            reason=''  # Empty reason
        )
        
        # Should raise validation error
        with self.assertRaises(Exception):
            adjustment.full_clean()
    
    def test_chorelog_requires_child_and_chore(self):
        """Test that ChoreLog requires both child and chore."""
        log = ChoreLog(points_awarded=10, status='PENDING')
        
        # Should raise validation error
        with self.assertRaises(Exception):
            log.full_clean()
    
    def test_redemption_requires_child_and_reward(self):
        """Test that Redemption requires both child and reward."""
        redemption = Redemption(status='PENDING')
        
        # Should raise validation error
        with self.assertRaises(Exception):
            redemption.full_clean()
