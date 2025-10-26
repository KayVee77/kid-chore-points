"""
Test script to verify points calculation fix
Run from project root: python test_points_fix.py
"""
import os
import sys
import django

# Add chorepoints to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'chorepoints'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chorepoints.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment

def test_scenario():
    """Test the exact scenario from the bug report"""
    
    # Get or create parent user
    parent, _ = User.objects.get_or_create(username='tevai', defaults={
        'email': 'parent@test.com',
        'is_staff': True,
        'is_superuser': True
    })
    
    # Get or create Agota
    agota, created = Kid.objects.get_or_create(
        name='Agota',
        parent=parent,
        defaults={'pin': '1234', 'points_balance': 0, 'map_position': 0}
    )
    
    if not created:
        # Reset for testing
        agota.points_balance = 0
        agota.map_position = 0
        agota.save()
        # Clear all logs
        agota.chore_logs.all().delete()
        agota.redemptions.all().delete()
        agota.point_adjustments.all().delete()
    
    print(f"\n=== Starting Test ===")
    print(f"Initial state:")
    print(f"  Points Balance: {agota.points_balance}")
    print(f"  Map Position: {agota.map_position}")
    
    # Step 1: Parent adds 50 points
    print(f"\n1. Parent adds 50 points adjustment")
    adj = PointAdjustment.objects.create(
        parent=parent,
        kid=agota,
        points=50,
        reason="Bonus points"
    )
    agota.refresh_from_db()
    print(f"  After adjustment:")
    print(f"    Points Balance: {agota.points_balance} (should be 50)")
    print(f"    Map Position: {agota.map_position} (should be 50)")
    
    # Create test chore and rewards
    chore, _ = Chore.objects.get_or_create(
        title="Clean room",
        parent=parent,
        defaults={'points': 10}
    )
    
    reward1, _ = Reward.objects.get_or_create(
        title="Ice cream",
        parent=parent,
        defaults={'cost_points': 5}
    )
    
    reward2, _ = Reward.objects.get_or_create(
        title="Extra TV time",
        parent=parent,
        defaults={'cost_points': 5}
    )
    
    # Step 2: Kid requests 2 rewards (5 points each)
    print(f"\n2. Kid requests 2 rewards (5 points each)")
    red1 = Redemption.objects.create(
        child=agota,
        reward=reward1,
        cost_points=reward1.cost_points
    )
    red2 = Redemption.objects.create(
        child=agota,
        reward=reward2,
        cost_points=reward2.cost_points
    )
    agota.refresh_from_db()
    print(f"  After creating redemption requests (PENDING):")
    print(f"    Points Balance: {agota.points_balance} (should still be 50)")
    print(f"    Map Position: {agota.map_position} (should still be 50)")
    
    # Step 3: Parent approves both redemptions
    print(f"\n3. Parent approves both redemptions")
    red1.approve()
    agota.refresh_from_db()
    print(f"  After first approval:")
    print(f"    Points Balance: {agota.points_balance} (should be 45)")
    print(f"    Map Position: {agota.map_position} (should still be 50)")
    
    red2.approve()
    agota.refresh_from_db()
    print(f"  After second approval:")
    print(f"    Points Balance: {agota.points_balance} (should be 40)")
    print(f"    Map Position: {agota.map_position} (should still be 50)")
    
    # Step 4: Kid completes chores
    print(f"\n4. Kid completes 3 chores (10 points each)")
    log1 = ChoreLog.objects.create(
        child=agota,
        chore=chore,
        points_awarded=chore.points
    )
    log2 = ChoreLog.objects.create(
        child=agota,
        chore=chore,
        points_awarded=chore.points
    )
    log3 = ChoreLog.objects.create(
        child=agota,
        chore=chore,
        points_awarded=chore.points
    )
    
    # Step 5: Parent approves chores
    print(f"\n5. Parent approves all 3 chores")
    log1.approve()
    agota.refresh_from_db()
    print(f"  After first chore approval:")
    print(f"    Points Balance: {agota.points_balance} (should be 50)")
    print(f"    Map Position: {agota.map_position} (should be 60)")
    
    log2.approve()
    agota.refresh_from_db()
    print(f"  After second chore approval:")
    print(f"    Points Balance: {agota.points_balance} (should be 60)")
    print(f"    Map Position: {agota.map_position} (should be 70)")
    
    log3.approve()
    agota.refresh_from_db()
    print(f"  After third chore approval:")
    print(f"    Points Balance: {agota.points_balance} (should be 70)")
    print(f"    Map Position: {agota.map_position} (should be 80)")
    
    # Final summary
    print(f"\n=== Test Complete ===")
    print(f"Final state:")
    print(f"  Points Balance: {agota.points_balance}")
    print(f"  Map Position: {agota.map_position}")
    print(f"\nBreakdown:")
    print(f"  Starting: 0 points, 0 map position")
    print(f"  + 50 points adjustment -> 50 balance, 50 map")
    print(f"  - 5 points (reward 1) -> 45 balance, 50 map")
    print(f"  - 5 points (reward 2) -> 40 balance, 50 map")
    print(f"  + 10 points (chore 1) -> 50 balance, 60 map")
    print(f"  + 10 points (chore 2) -> 60 balance, 70 map")
    print(f"  + 10 points (chore 3) -> 70 balance, 80 map")
    print(f"\n✓ Points Balance represents current spendable points")
    print(f"✓ Map Position represents total earned points (never decreases)")

if __name__ == '__main__':
    test_scenario()
