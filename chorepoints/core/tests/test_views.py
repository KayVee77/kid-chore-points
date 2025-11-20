"""
Unit tests for core views.

Tests cover:
- Kid login view: PIN authentication, session management
- Kid home view: display of points, chores, rewards
- Chore submission view: creating ChoreLog records
- Reward redemption view: creating Redemption records
- PIN change view: updating kid PIN
- Landing page view: display and navigation
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Kid, Chore, Reward, ChoreLog, Redemption


class LandingPageViewTests(TestCase):
    """Test landing page view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_landing_page_loads(self):
        """Test landing page returns 200 OK."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_landing_page_content(self):
        """Test landing page contains expected content."""
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Taškų Nuotykis')


class KidLoginViewTests(TestCase):
    """Test kid login view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=0
        )
    
    def test_login_page_loads(self):
        """Test login page returns 200 OK."""
        response = self.client.get(reverse('kid_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kid/login.html')
    
    def test_login_with_correct_pin(self):
        """Test successful login with correct PIN."""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertRedirects(response, reverse('kid_home'))
        
        # Check session was set
        self.assertEqual(self.client.session['kid_id'], self.kid.id)
    
    def test_login_with_incorrect_pin(self):
        """Test login fails with incorrect PIN."""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '9999'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Neteisingas PIN')  # Error message
        
        # Check session was not set
        self.assertNotIn('kid_id', self.client.session)
    
    def test_login_with_inactive_kid(self):
        """Test login fails for inactive kid."""
        self.kid.active = False
        self.kid.save()
        
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('kid_id', self.client.session)
    
    def test_login_with_nonexistent_kid(self):
        """Test login fails for non-existent kid."""
        response = self.client.post(reverse('kid_login'), {
            'kid': 99999,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('kid_id', self.client.session)


class KidHomeViewTests(TestCase):
    """Test kid home view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=50
        )
        self.chore = Chore.objects.create(
            title='Test Chore',
            points=10,
            parent=self.user
        )
        self.reward = Reward.objects.create(
            title='Test Reward',
            cost_points=20,
            parent=self.user
        )
    
    def test_home_requires_login(self):
        """Test home page redirects if not logged in."""
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, reverse('kid_login'))
    
    def test_home_displays_points_balance(self):
        """Test home page displays kid's points balance."""
        # Log in
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50')  # Points balance
        self.assertContains(response, 'TestKid')  # Kid name
    
    def test_home_displays_available_chores(self):
        """Test home page displays available chores."""
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        
        response = self.client.get(reverse('kid_home'))
        self.assertContains(response, 'Test Chore')
        self.assertContains(response, '10')  # Chore points
    
    def test_home_displays_available_rewards(self):
        """Test home page displays available rewards."""
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        
        response = self.client.get(reverse('kid_home'))
        self.assertContains(response, 'Test Reward')
        self.assertContains(response, '20')  # Reward cost
    
    def test_rewards_banner_hidden_until_all_milestones_done(self):
        """Completion banner should not show before final milestone."""
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        self.kid.map_position = 100
        self.kid.save(update_fields=['map_position'])
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pasiekei visus apdovanojimus!")
    
    def test_rewards_banner_shows_after_final_milestone(self):
        """Completion banner should appear once all milestones are reached."""
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        self.kid.map_position = 3000
        self.kid.save(update_fields=['map_position'])
        
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pasiekei visus apdovanojimus!")


class ChoreSubmissionViewTests(TestCase):
    """Test chore submission view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
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
        
        # Log in
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_submit_chore_creates_pending_log(self):
        """Test submitting a chore creates PENDING ChoreLog."""
        response = self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirect after submit
        
        # Check ChoreLog was created
        log = ChoreLog.objects.filter(child=self.kid, chore=self.chore).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'PENDING')
        self.assertEqual(log.points_awarded, 15)
        
        # Check points not added yet (still pending)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
    
    def test_submit_chore_requires_login(self):
        """Test submitting chore requires authentication."""
        # Log out
        self.client.session.flush()
        
        response = self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(ChoreLog.objects.count(), 0)  # No log created
    
    def test_duplicate_pending_chore_prevented(self):
        """Test cannot submit same chore twice while pending."""
        # Submit first time
        self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        # Try to submit again
        response = self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        # Should only have one ChoreLog
        self.assertEqual(ChoreLog.objects.filter(child=self.kid, chore=self.chore).count(), 1)
    
    def test_submit_nonexistent_chore(self):
        """Test submitting non-existent chore fails gracefully."""
        response = self.client.post(reverse('complete_chore', args=[99999]))
        
        self.assertEqual(ChoreLog.objects.count(), 0)


class RewardRedemptionViewTests(TestCase):
    """Test reward redemption view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=100
        )
        self.reward = Reward.objects.create(
            title='Ice Cream',
            cost_points=30,
            parent=self.user
        )
        
        # Log in
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_redeem_reward_creates_pending_redemption(self):
        """Test redeeming a reward creates PENDING Redemption."""
        response = self.client.post(reverse('redeem_reward', args=[self.reward.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirect after submit
        
        # Check Redemption was created
        redemption = Redemption.objects.filter(child=self.kid, reward=self.reward).first()
        self.assertIsNotNone(redemption)
        self.assertEqual(redemption.status, 'PENDING')
        self.assertEqual(redemption.cost_points, 30)
        
        # Check points not deducted yet (still pending)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 100)
    
    def test_redeem_reward_requires_login(self):
        """Test redeeming reward requires authentication."""
        # Log out
        self.client.session.flush()
        
        response = self.client.post(reverse('redeem_reward', args=[self.reward.id]))
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Redemption.objects.count(), 0)  # No redemption created
    
    def test_duplicate_pending_redemption_prevented(self):
        """Test cannot redeem same reward twice while pending."""
        # Redeem first time
        self.client.post(reverse('redeem_reward', args=[self.reward.id]))
        
        # Try to redeem again
        response = self.client.post(reverse('redeem_reward', args=[self.reward.id]))
        
        # Should only have one Redemption
        self.assertEqual(Redemption.objects.filter(child=self.kid, reward=self.reward).count(), 1)
    
    def test_redeem_nonexistent_reward(self):
        """Test redeeming non-existent reward fails gracefully."""
        response = self.client.post(reverse('redeem_reward', args=[99999]))
        
        self.assertEqual(Redemption.objects.count(), 0)


class PINChangeViewTests(TestCase):
    """Test PIN change view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=0
        )
        
        # Log in
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_pin_change_page_loads(self):
        """Test PIN change page returns 200 OK."""
        response = self.client.get(reverse('change_pin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kid/change_pin.html')
    
    def test_pin_change_requires_login(self):
        """Test PIN change requires authentication."""
        # Log out
        self.client.session.flush()
        
        response = self.client.get(reverse('change_pin'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, reverse('kid_login'))
    
    def test_change_pin_with_correct_old_pin(self):
        """Test changing PIN with correct old PIN."""
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect on success
        
        # Check PIN was updated
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '5678')
    
    def test_change_pin_with_incorrect_old_pin(self):
        """Test changing PIN fails with incorrect old PIN."""
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '9999',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        
        self.assertEqual(response.status_code, 200)  # Stay on page
        
        # Check PIN was not updated
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '1234')
    
    def test_change_pin_with_mismatched_new_pins(self):
        """Test changing PIN fails if new PINs don't match."""
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '9999'
        })
        
        self.assertEqual(response.status_code, 200)  # Stay on page
        
        # Check PIN was not updated
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '1234')


class SessionManagementTests(TestCase):
    """Test session management across views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username='testparent', password='testpass123')
        self.kid = Kid.objects.create(
            name='TestKid',
            parent=self.user,
            pin='1234',
            points_balance=50
        )
    
    def test_login_sets_session(self):
        """Test login sets kid_id in session."""
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        self.assertEqual(self.client.session['kid_id'], self.kid.id)
    
    def test_logout_clears_session(self):
        """Test logout clears session."""
        # Log in first
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
        
        # Log out
        response = self.client.get(reverse('kid_logout'))
        
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertNotIn('kid_id', self.client.session)
    
    def test_multiple_requests_maintain_session(self):
        """Test session persists across multiple requests."""
        # Log in
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Make multiple requests
        self.client.get(reverse('kid_home'))
        self.client.get(reverse('change_pin'))
        
        # Session should still be valid
        self.assertEqual(self.client.session['kid_id'], self.kid.id)
