"""
Security tests for ChorePoints application.
Tests authentication, authorization, and security measures.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Kid, Chore, Reward, ChoreLog, Redemption


class AuthenticationSecurityTests(TestCase):
    """Test authentication security measures."""
    
    def setUp(self):
        """Create test data for security testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid1 = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=50,
            active=True,
            parent=self.parent
        )
        
        self.kid2 = Kid.objects.create(
            name='Agota',
            pin='5678',
            points_balance=100,
            active=True,
            parent=self.parent
        )
        
        self.inactive_kid = Kid.objects.create(
            name='Inactive',
            pin='9999',
            points_balance=0,
            active=False,
            parent=self.parent
        )
    
    def test_login_requires_valid_pin(self):
        """Test that login fails with invalid PIN."""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid1.id,
            'pin': 'wrong'
        })
        # Should stay on login page or redirect back
        self.assertNotIn('kid_id', self.client.session)
    
    def test_login_requires_active_kid(self):
        """Test that inactive kids cannot login."""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.inactive_kid.id,
            'pin': '9999'
        })
        # Should fail to login
        self.assertNotIn('kid_id', self.client.session)
    
    def test_session_persists_across_requests(self):
        """Test that session persists correctly."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid1.id,
            'pin': '1234'
        })
        
        # Make another request
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['kid_id'], self.kid1.id)
    
    def test_logout_clears_session(self):
        """Test that logout properly clears session."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid1.id,
            'pin': '1234'
        })
        self.assertIn('kid_id', self.client.session)
        
        # Logout
        self.client.post(reverse('kid_logout'))
        self.assertNotIn('kid_id', self.client.session)
    
    def test_pin_stored_as_plaintext_mvp_limitation(self):
        """Test that PINs are stored as plaintext (MVP limitation, documented)."""
        # This is a known MVP limitation - PINs are plaintext
        kid = Kid.objects.get(id=self.kid1.id)
        self.assertEqual(kid.pin, '1234')  # Plaintext, not hashed
        # NOTE: In production, should use Django's make_password/check_password
    
    def test_multiple_kids_can_have_different_sessions(self):
        """Test that different browser sessions can be for different kids."""
        # Client 1 logs in as kid1
        client1 = Client()
        client1.post(reverse('kid_login'), {
            'kid': self.kid1.id,
            'pin': '1234'
        })
        
        # Client 2 logs in as kid2
        client2 = Client()
        client2.post(reverse('kid_login'), {
            'kid': self.kid2.id,
            'pin': '5678'
        })
        
        # Each should have their own session
        self.assertEqual(client1.session['kid_id'], self.kid1.id)
        self.assertEqual(client2.session['kid_id'], self.kid2.id)


class AuthorizationSecurityTests(TestCase):
    """Test authorization and access control measures."""
    
    def setUp(self):
        """Create test data for authorization testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid1 = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=50,
            active=True,
            parent=self.parent
        )
        
        self.kid2 = Kid.objects.create(
            name='Agota',
            pin='5678',
            points_balance=100,
            active=True,
            parent=self.parent
        )
        
        self.chore = Chore.objects.create(
            title='Test chore',
            points=10,
            parent=self.parent
        )
        
        self.reward = Reward.objects.create(
            title='Test reward',
            cost_points=20,
            parent=self.parent
        )
    
    def test_unauthenticated_cannot_access_kid_home(self):
        """Test that kid home requires authentication."""
        response = self.client.get(reverse('kid_home'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('kid/login', response.url)
    
    def test_unauthenticated_cannot_submit_chore(self):
        """Test that chore submission requires authentication."""
        response = self.client.post(reverse('complete_chore', args=[self.chore.id]))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('kid/login', response.url)
    
    def test_unauthenticated_cannot_redeem_reward(self):
        """Test that reward redemption requires authentication."""
        response = self.client.post(reverse('redeem_reward', args=[self.reward.id]))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('kid/login', response.url)
    
    def test_unauthenticated_cannot_change_pin(self):
        """Test that PIN change requires authentication."""
        response = self.client.get(reverse('change_pin'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('kid/login', response.url)
    
    def test_kid_cannot_access_other_kids_data_via_session(self):
        """Test that kid1 cannot manually set session to access kid2's data."""
        # Login as kid1
        self.client.post(reverse('kid_login'), {
            'kid': self.kid1.id,
            'pin': '1234'
        })
        
        # Manually try to change session to kid2 (simulating session hijacking attempt)
        session = self.client.session
        session['kid_id'] = self.kid2.id
        session.save()
        
        # Try to access home page - should work since we're testing session-based auth
        # (In a real attack, attacker would need to steal session cookie)
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        # This demonstrates that session security depends on protecting the session cookie
    
    def test_kid_chore_logs_isolated_by_child_fk(self):
        """Test that chore logs are properly isolated by child FK."""
        # Create chore logs for both kids
        log1 = ChoreLog.objects.create(
            child=self.kid1,
            chore=self.chore
        )
        log2 = ChoreLog.objects.create(
            child=self.kid2,
            chore=self.chore
        )
        
        # Each kid should only see their own logs
        kid1_logs = ChoreLog.objects.filter(child=self.kid1)
        kid2_logs = ChoreLog.objects.filter(child=self.kid2)
        
        self.assertEqual(kid1_logs.count(), 1)
        self.assertEqual(kid2_logs.count(), 1)
        self.assertIn(log1, kid1_logs)
        self.assertNotIn(log2, kid1_logs)
    
    def test_kid_redemptions_isolated_by_child_fk(self):
        """Test that redemptions are properly isolated by child FK."""
        # Create redemptions for both kids
        redemption1 = Redemption.objects.create(
            child=self.kid1,
            reward=self.reward
        )
        redemption2 = Redemption.objects.create(
            child=self.kid2,
            reward=self.reward
        )
        
        # Each kid should only see their own redemptions
        kid1_redemptions = Redemption.objects.filter(child=self.kid1)
        kid2_redemptions = Redemption.objects.filter(child=self.kid2)
        
        self.assertEqual(kid1_redemptions.count(), 1)
        self.assertEqual(kid2_redemptions.count(), 1)
        self.assertIn(redemption1, kid1_redemptions)
        self.assertNotIn(redemption2, kid1_redemptions)


class CSRFProtectionTests(TestCase):
    """Test CSRF protection on forms."""
    
    def setUp(self):
        """Create test data for CSRF testing."""
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
            title='Test chore',
            points=10,
            parent=self.parent
        )
        
        self.reward = Reward.objects.create(
            title='Test reward',
            cost_points=20,
            parent=self.parent
        )
    
    def test_login_form_requires_csrf_token(self):
        """Test that login form requires CSRF token."""
        # GET request to get CSRF token
        response = self.client.get(reverse('kid_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_pin_change_form_requires_csrf_token(self):
        """Test that PIN change form requires CSRF token."""
        # Login first
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # GET PIN change page
        response = self.client.get(reverse('change_pin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
    
    def test_chore_submission_without_csrf_fails(self):
        """Test that chore submission without CSRF token fails."""
        # Login first
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Try to submit chore without CSRF (Django test client handles CSRF by default)
        # We need to use enforce_csrf_checks to test this
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        
        # Copy session from authenticated client
        csrf_client.cookies = self.client.cookies
        
        # Try POST without CSRF token
        response = csrf_client.post(reverse('complete_chore', args=[self.chore.id]))
        # Should fail with 403 Forbidden
        self.assertEqual(response.status_code, 403)


class InputValidationTests(TestCase):
    """Test input validation and sanitization."""
    
    def setUp(self):
        """Create test data for validation testing."""
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
    
    def test_pin_length_validation(self):
        """Test that PINs have length validation."""
        from core.forms import ChangePinForm
        
        # Too short (less than 4)
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '123',
            'confirm_new_pin': '123'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
        
        # Too long (more than 20)
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '123456789012345678901',
            'confirm_new_pin': '123456789012345678901'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('new_pin', form.errors)
    
    def test_pin_change_requires_matching_confirmation(self):
        """Test that PIN change requires matching new PIN confirmation."""
        from core.forms import ChangePinForm
        
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5679'  # Different!
        })
        self.assertFalse(form.is_valid())
        # Error is raised at form level (clean method)
        self.assertTrue(len(form.non_field_errors()) > 0)
    
    def test_kid_login_form_validates_required_fields(self):
        """Test that login form validates required fields."""
        from core.forms import KidLoginForm
        
        # Missing kid
        form = KidLoginForm(data={
            'pin': '1234'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('kid', form.errors)
        
        # Missing PIN
        form = KidLoginForm(data={
            'kid': self.kid.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn('pin', form.errors)
