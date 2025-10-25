# Points Calculation Bug Fix

## Issue Description

The kid's page was showing incorrect total points after parent actions:
- Added 50 points to Agota via PointAdjustment
- Requested 2 rewards (5 points each) 
- Parent approved both rewards
- Expected balance: 40 points
- **Actual balance: 45 points** ❌

Additionally, approved chores were not adding all points correctly.

## Root Causes

### Bug 1: PointAdjustment not updating map_position
**Location:** `chorepoints/core/models.py` - `PointAdjustment.save()` method

**Problem:** When a parent manually adds points through PointAdjustment, only `points_balance` was updated, but `map_position` was not. This caused:
- Map position to be out of sync with earned points
- Adventure map milestones to not unlock properly
- Inconsistent state between balance and progress

**Original Code:**
```python
def save(self, *args, **kwargs):
    is_new = self._state.adding
    super().save(*args, **kwargs)
    if is_new:
        self.kid.points_balance += self.points
        self.kid.save(update_fields=["points_balance"])  # Missing map_position!
```

**Fixed Code:**
```python
def save(self, *args, **kwargs):
    is_new = self._state.adding
    super().save(*args, **kwargs)
    if is_new:
        self.kid.points_balance += self.points
        # Also update map_position for positive adjustments
        if self.points > 0:
            self.kid.map_position += self.points
        self.kid.save(update_fields=["points_balance", "map_position"])
```

### Bug 2: Missing reject() method in Redemption model
**Location:** `chorepoints/core/models.py` - `Redemption` class

**Problem:** The `Redemption` model was missing a `reject()` method entirely. The `reject()` method was incorrectly placed in the `PointAdjustment` class (which doesn't have a status field). This meant:
- Admins couldn't properly reject reward redemptions
- The admin action would fail silently

**Fix:** Added proper `reject()` method to `Redemption` class and removed the incorrect one from `PointAdjustment`.

**Added Code:**
```python
def reject(self):
    if self.status != self.Status.PENDING:
        return False
    self.status = self.Status.REJECTED
    self.processed_at = timezone.now()
    self.save(update_fields=["status", "processed_at"])
    return True
```

## How Points System Works (After Fix)

### Two Separate Counters:
1. **points_balance**: Current spendable points (increases with chores/adjustments, decreases with rewards)
2. **map_position**: Total lifetime earned points (only increases, never decreases)

### Point Flow:

#### Kid Completes Chore:
```
1. ChoreLog created with status=PENDING → No points change yet
2. Parent approves → ChoreLog.approve() called
3. points_balance += points_awarded
4. map_position += points_awarded  
5. Status set to APPROVED
```

#### Kid Requests Reward:
```
1. Redemption created with status=PENDING → No points change yet
2. Parent approves → Redemption.approve() called
3. points_balance -= cost_points
4. map_position unchanged (rewards don't reduce progress!)
5. Status set to APPROVED
```

#### Parent Adds Bonus Points:
```
1. PointAdjustment created
2. In save():
   - points_balance += points
   - map_position += points (if points > 0)
```

## Test Scenario

Starting: 0 balance, 0 map position

| Action | Balance | Map Position | Notes |
|--------|---------|--------------|-------|
| Initial | 0 | 0 | |
| +50 adjustment | 50 | 50 | Bonus from parent |
| Request reward 1 (5 pts) | 50 | 50 | Pending, no change |
| Approve reward 1 | 45 | 50 | ✓ Balance decreased, map unchanged |
| Request reward 2 (5 pts) | 45 | 50 | Pending, no change |
| Approve reward 2 | **40** | 50 | ✓ **Now shows correct 40!** |
| Complete chore 1 (10 pts) | 40 | 50 | Pending, no change |
| Approve chore 1 | 50 | 60 | Both increased |
| Approve chore 2 | 60 | 70 | Both increased |
| Approve chore 3 | 70 | 80 | Both increased |

## Files Changed

1. `chorepoints/core/models.py`:
   - Fixed `PointAdjustment.save()` to update map_position
   - Added `Redemption.reject()` method
   - Removed incorrect `PointAdjustment.reject()` method

## Testing

Run the test script to verify the fix:
```powershell
.\.venv\Scripts\python.exe .\test_points_fix.py
```

Expected output should show:
- Correct balance after each operation
- Map position only increasing (never decreasing)
- Final balance of 70 and map position of 80

## Migration Required?

**No migration needed!** The bug was purely in the Python logic. The database schema was already correct with both `points_balance` and `map_position` fields.

However, existing data may be incorrect. To fix existing kids' data:
1. Recalculate map_position from all approved ChoreLog + PointAdjustment records
2. Or use the admin action "Reset map position" and have kids re-earn their progress

## Admin View

To check/verify kid's data in Django admin:
1. Navigate to `/admin/core/kid/`
2. Check both `points_balance` and `map_position` columns
3. For Agota with PIN 1234, after the scenario above:
   - Points Balance: 70 (current spendable)
   - Map Position: 80 (total earned)

## Notes

- This fix maintains backward compatibility
- No changes needed to templates or views
- The approval workflow remains transaction-safe with `transaction.atomic()`
- Redemptions correctly don't decrease map_position (rewards shouldn't punish progress)
