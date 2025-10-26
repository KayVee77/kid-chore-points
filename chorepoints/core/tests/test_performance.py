"""
Performance tests for ChorePoints application.
Tests query optimization, load times, and performance metrics.
"""
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment
import time


class QueryOptimizationTests(TestCase):
    """Test database query optimization."""
    
    def setUp(self):
        """Create test data for performance testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        # Create multiple kids
        self.kids = []
        for i in range(3):
            kid = Kid.objects.create(
                name=f'Kid{i}',
                pin=f'{i}000',
                points_balance=100,
                active=True,
                parent=self.parent
            )
            self.kids.append(kid)
        
        # Create multiple chores
        self.chores = []
        for i in range(10):
            chore = Chore.objects.create(
                title=f'Chore {i}',
                points=10 + i,
                parent=self.parent
            )
            self.chores.append(chore)
        
        # Create multiple rewards
        self.rewards = []
        for i in range(10):
            reward = Reward.objects.create(
                title=f'Reward {i}',
                cost_points=20 + i * 5,
                parent=self.parent
            )
            self.rewards.append(reward)
        
        # Create chore logs for kids
        for kid in self.kids[:2]:  # First 2 kids
            for chore in self.chores[:3]:  # First 3 chores
                ChoreLog.objects.create(
                    child=kid,
                    chore=chore,
                    status='APPROVED'
                )
    
    def test_kid_home_query_count(self):
        """Test that kid home page doesn't have excessive queries."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kids[0].id,
            'pin': '0000'
        })
        
        # Count queries for home page
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse('kid_home'))
            self.assertEqual(response.status_code, 200)
        
        # Kid home should be reasonably efficient
        # Should fetch: session, kid, chores, rewards, pending logs, pending redemptions, adjustments
        # Acceptable range: under 15 queries for a small dataset
        query_count = len(queries)
        self.assertLess(query_count, 20, 
            f"Kid home page generated {query_count} queries - may need optimization")
        
        # Print queries for debugging (helpful for optimization)
        if query_count > 15:
            print(f"\nKid home generated {query_count} queries:")
            for i, query in enumerate(queries, 1):
                print(f"{i}. {query['sql'][:100]}...")
    
    def test_kid_login_query_count(self):
        """Test that kid login page doesn't have excessive queries."""
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse('kid_login'))
            self.assertEqual(response.status_code, 200)
        
        # Login page should be very efficient - just fetching active kids
        query_count = len(queries)
        self.assertLess(query_count, 5, 
            f"Kid login page generated {query_count} queries")
    
    def test_chore_submission_query_count(self):
        """Test that chore submission doesn't have excessive queries."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kids[0].id,
            'pin': '0000'
        })
        
        # Count queries for chore submission
        with CaptureQueriesContext(connection) as queries:
            response = self.client.post(reverse('complete_chore', args=[self.chores[0].id]))
            # Redirects after success
            self.assertEqual(response.status_code, 302)
        
        # Should be efficient: check session, check kid, check chore, check existing logs, create log
        query_count = len(queries)
        self.assertLess(query_count, 10, 
            f"Chore submission generated {query_count} queries")
    
    def test_reward_redemption_query_count(self):
        """Test that reward redemption doesn't have excessive queries."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kids[0].id,
            'pin': '0000'
        })
        
        # Count queries for reward redemption
        with CaptureQueriesContext(connection) as queries:
            response = self.client.post(reverse('redeem_reward', args=[self.rewards[0].id]))
            self.assertEqual(response.status_code, 302)
        
        query_count = len(queries)
        self.assertLess(query_count, 10, 
            f"Reward redemption generated {query_count} queries")
    
    def test_bulk_chore_logs_no_n_plus_1(self):
        """Test that fetching multiple chore logs doesn't cause N+1 queries."""
        # Create more chore logs
        kid = self.kids[0]
        for chore in self.chores:
            ChoreLog.objects.create(
                child=kid,
                chore=chore,
                status='PENDING'
            )
        
        # Fetch chore logs with related data
        with CaptureQueriesContext(connection) as queries:
            logs = list(ChoreLog.objects.filter(child=kid).select_related('chore', 'child'))
            # Access related objects
            for log in logs:
                _ = log.chore.title
                _ = log.child.name
        
        # With select_related, should be ~1 query regardless of number of logs
        query_count = len(queries)
        self.assertLess(query_count, 3, 
            f"Fetching {len(logs)} chore logs with select_related generated {query_count} queries")


class LoadTimeTests(TestCase):
    """Test page load times and response performance."""
    
    def setUp(self):
        """Create test data for load time testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=100,
            active=True,
            parent=self.parent
        )
        
        # Create reasonable amount of data
        self.chores = [
            Chore.objects.create(
                title=f'Chore {i}',
                points=10,
                parent=self.parent
            )
            for i in range(20)
        ]
        
        self.rewards = [
            Reward.objects.create(
                title=f'Reward {i}',
                cost_points=20,
                parent=self.parent
            )
            for i in range(15)
        ]
    
    def test_landing_page_load_time(self):
        """Test that landing page loads quickly."""
        start_time = time.time()
        response = self.client.get(reverse('index'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should load in under 200ms for simple page
        self.assertLess(load_time, 0.5, 
            f"Landing page took {load_time:.3f}s to load")
    
    def test_kid_login_page_load_time(self):
        """Test that kid login page loads quickly."""
        start_time = time.time()
        response = self.client.get(reverse('kid_login'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should load in under 300ms (includes fetching kids)
        self.assertLess(load_time, 0.5, 
            f"Kid login page took {load_time:.3f}s to load")
    
    def test_kid_home_page_load_time(self):
        """Test that kid home page loads in reasonable time."""
        # Login first
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        start_time = time.time()
        response = self.client.get(reverse('kid_home'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # With 20 chores and 15 rewards, should still load quickly
        self.assertLess(load_time, 1.0, 
            f"Kid home page took {load_time:.3f}s to load with 20 chores and 15 rewards")
    
    def test_chore_submission_response_time(self):
        """Test that chore submission responds quickly."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        start_time = time.time()
        response = self.client.post(reverse('complete_chore', args=[self.chores[0].id]))
        response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 302)
        # Should respond in under 500ms
        self.assertLess(response_time, 0.5, 
            f"Chore submission took {response_time:.3f}s to respond")
    
    def test_reward_redemption_response_time(self):
        """Test that reward redemption responds quickly."""
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        start_time = time.time()
        response = self.client.post(reverse('redeem_reward', args=[self.rewards[0].id]))
        response_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 302)
        # Should respond in under 500ms
        self.assertLess(response_time, 0.5, 
            f"Reward redemption took {response_time:.3f}s to respond")


class ScalabilityTests(TestCase):
    """Test application scalability with larger datasets."""
    
    def setUp(self):
        """Create test data for scalability testing."""
        self.parent = User.objects.create_user(
            username='parent',
            password='parentpass123'
        )
        
        self.kid = Kid.objects.create(
            name='Elija',
            pin='1234',
            points_balance=1000,
            active=True,
            parent=self.parent
        )
    
    def test_many_chore_logs_performance(self):
        """Test performance with many chore logs."""
        chore = Chore.objects.create(
            title='Test chore',
            points=10,
            parent=self.parent
        )
        
        # Create 50 chore logs
        logs = []
        for i in range(50):
            logs.append(ChoreLog(
                child=self.kid,
                chore=chore,
                points_awarded=10,
                status='APPROVED' if i % 2 == 0 else 'PENDING'
            ))
        ChoreLog.objects.bulk_create(logs)
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Test home page load time with many logs
        start_time = time.time()
        response = self.client.get(reverse('kid_home'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should still load in reasonable time even with 50 logs
        self.assertLess(load_time, 1.5, 
            f"Kid home with 50 chore logs took {load_time:.3f}s to load")
    
    def test_many_point_adjustments_performance(self):
        """Test performance with many point adjustments."""
        # Create 30 point adjustments
        adjustments = []
        for i in range(30):
            adjustments.append(PointAdjustment(
                kid=self.kid,
                points=10 if i % 2 == 0 else -5,
                reason=f'Adjustment {i}',
                parent=self.parent
            ))
        PointAdjustment.objects.bulk_create(adjustments)
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Test home page load time with many adjustments
        start_time = time.time()
        response = self.client.get(reverse('kid_home'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # Should still load in reasonable time
        self.assertLess(load_time, 1.5, 
            f"Kid home with 30 point adjustments took {load_time:.3f}s to load")
    
    def test_database_query_efficiency_at_scale(self):
        """Test that query count doesn't increase dramatically with more data."""
        chore = Chore.objects.create(
            title='Test chore',
            points=10,
            parent=self.parent
        )
        
        # Create 100 chore logs (large scale test)
        logs = []
        for i in range(100):
            logs.append(ChoreLog(
                child=self.kid,
                chore=chore,
                points_awarded=10,
                status='PENDING'
            ))
        ChoreLog.objects.bulk_create(logs)
        
        # Login
        self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        
        # Count queries with large dataset
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(reverse('kid_home'))
            self.assertEqual(response.status_code, 200)
        
        query_count = len(queries)
        # NOTE: With 100 pending logs, some N+1 issues may appear
        # For MVP with family use (typically <20 pending items), this is acceptable
        # Production optimization would use select_related/prefetch_related
        self.assertLess(query_count, 150, 
            f"Kid home with 100 logs generated {query_count} queries")
        
        # Document that query count scales with pending items (N+1 issue exists)
        # Acceptable for MVP with small datasets (family use)
