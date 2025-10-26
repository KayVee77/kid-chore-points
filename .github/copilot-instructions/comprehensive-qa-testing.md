# Comprehensive QA Testing Instructions for ChorePoints App

## Mission
Perform exhaustive quality assurance testing of the ChorePoints Django application to ensure zero bugs, complete functionality, and production readiness. Use all available tools including MCP Playwright for browser automation, MCP Pylance for Python code analysis, and manual testing.

## Testing Objectives

1. **Code Quality Analysis** - Verify code structure, imports, syntax
2. **Functional Testing** - Test all features end-to-end
3. **Browser Automation** - Test user workflows with Playwright
4. **Unit Testing** - Create and run comprehensive unit tests
5. **Integration Testing** - Test component interactions
6. **Security Testing** - Verify authentication, authorization, data protection
7. **Performance Testing** - Check response times, database queries
8. **Cross-Device Testing** - Test on desktop and mobile browsers

## Tools & Resources

### Available Tools
- **MCP Pylance**: Python code analysis, syntax validation, import checking
- **MCP Playwright**: Browser automation, visual testing, user flow simulation
- **Django Test Framework**: Unit and integration tests
- **Python Scripts**: Custom validation scripts in `chorepoints/` directory

### Project Structure
```
chorepoints/
├── core/                    # Main Django app
│   ├── models.py           # Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment
│   ├── views.py            # All view functions
│   ├── admin.py            # Django admin customizations
│   ├── forms.py            # KidLoginForm, ChangePinForm
│   ├── urls.py             # URL routing
│   └── templates/          # HTML templates
├── chorepoints/
│   ├── settings.py         # Django settings
│   └── urls.py             # Root URL config
├── manage.py               # Django management
├── dev.ps1                 # Development setup script
├── run.ps1                 # HTTP server launcher
└── run_https.ps1           # HTTPS server launcher
```

## Phase 1: Code Quality Analysis with MCP Pylance

### Task 1.1: Analyze Python Files for Syntax Errors

Use `pylanceSyntaxErrors` to check all Python files:

```
Check these files for syntax errors:
- chorepoints/core/models.py
- chorepoints/core/views.py
- chorepoints/core/admin.py
- chorepoints/core/forms.py
- chorepoints/core/urls.py
- chorepoints/chorepoints/settings.py
- chorepoints/chorepoints/urls.py
- chorepoints/manage.py
```

**Expected Result**: No syntax errors

**Action if errors found**: Document errors and fix immediately

### Task 1.2: Verify Imports and Dependencies

Use `pylanceImports` to analyze workspace imports:

```
Analyze all imports across workspace
Check for:
- Missing dependencies
- Unresolved imports
- Circular dependencies
- Unused imports
```

**Expected Result**: All imports resolve correctly

**Action if issues found**: Add missing packages or fix import paths

### Task 1.3: Check Installed Packages

Use `pylanceInstalledTopLevelModules` to verify environment:

```
Verify these packages are installed:
- Django (>=5.0,<5.3)
- Pillow (>=10.4,<11.0)
- django-extensions (>=3.2,<4.0)
- werkzeug (>=3.0,<4.0)
- pyOpenSSL (>=24.0,<25.0)
```

**Expected Result**: All required packages present

**Action if missing**: Install missing packages via pip

### Task 1.4: Run Code Snippet Validation

Use `pylanceRunCodeSnippet` to test critical functions:

```python
# Test 1: Verify Django imports
from django.conf import settings
from django.contrib.auth.models import User
from core.models import Kid, Chore, Reward
print("Django imports: OK")

# Test 2: Check database connection
from django.db import connection
connection.ensure_connection()
print("Database connection: OK")

# Test 3: Validate model methods exist
kid = Kid()
assert hasattr(kid, 'get_map_progress')
assert hasattr(kid, 'get_achievements')
print("Model methods: OK")
```

**Expected Result**: All snippets execute without errors

**Action if errors**: Fix import or configuration issues

## Phase 2: Browser Automation Testing with MCP Playwright

### Task 2.1: Setup and Launch Application

**Pre-requisites**:
1. Ensure Django server is running: `.\chorepoints\run.ps1` or `.\chorepoints\run_https.ps1`
2. URL: `http://127.0.0.1:8000` or `https://127.0.0.1:8000`

### Task 2.2: Landing Page Testing

Use Playwright to test landing page:

```
1. Navigate to http://127.0.0.1:8000/
2. Take screenshot of landing page
3. Verify elements exist:
   - "Taškų Nuotykis" title
   - "Vaikams" (Kids) link
   - "Tėvams" (Parents/Admin) link
4. Check page loads without console errors
```

**Expected Result**: Landing page loads correctly with all elements

**Test Script**:
```javascript
// Navigate to landing page
await page.goto('http://127.0.0.1:8000/');

// Take screenshot
await page.screenshot({ path: 'test-results/landing-page.png', fullPage: true });

// Verify title
const title = await page.title();
assert(title.includes('Taškų Nuotykis'));

// Check links
await page.getByText('Vaikams').click();
await page.waitForURL('**/kid/login/');
await page.goBack();
```

### Task 2.3: Kid Login Flow Testing

Test kid authentication with Playwright:

```
1. Navigate to /kid/login/
2. Test login with Elija (PIN: 1234)
3. Test login with Agota (PIN: 5678)
4. Test invalid PIN (should show error)
5. Test empty PIN (should show error)
6. Verify redirect to /kid/home/ on success
```

**Expected Results**:
- Valid PIN → Redirect to kid home
- Invalid PIN → Error message "Neteisingas PIN arba paskyra neaktyvi."
- Empty PIN → Form validation error

**Test Script**:
```javascript
// Test valid login - Elija
await page.goto('http://127.0.0.1:8000/kid/login/');
await page.click('[alt="Elija"]'); // Click kid profile
await page.click('button:has-text("1")');
await page.click('button:has-text("2")');
await page.click('button:has-text("3")');
await page.click('button:has-text("4")');
await page.click('button:has-text("✓ Prisijungti")');
await page.waitForURL('**/kid/home/');
expect(await page.textContent('body')).toContain('Sveikas, Elija');

// Test invalid PIN
await page.goto('http://127.0.0.1:8000/kid/logout/');
await page.goto('http://127.0.0.1:8000/kid/login/');
await page.click('[alt="Elija"]');
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("✓ Prisijungti")');
expect(await page.textContent('.errorlist, .alert-danger')).toContain('Neteisingas');
```

### Task 2.4: Kid Home Page Testing

Test kid dashboard functionality:

```
1. Login as Elija
2. Verify kid home page elements:
   - Welcome message: "Sveikas, Elija!"
   - Points balance displayed
   - Progress bar to next reward
   - Adventure map with milestones
   - Achievement badges
   - List of available chores
   - List of available rewards
   - Pending chores/rewards section
   - Recent approved items
   - Point adjustments from parents
3. Take screenshot of full page
```

**Expected Result**: All sections render correctly with data

**Test Script**:
```javascript
await page.goto('http://127.0.0.1:8000/kid/home/');

// Check welcome message
expect(await page.textContent('h2')).toContain('Sveikas, Elija');

// Check points badge
const pointsBadge = await page.locator('.points-badge, .badge').textContent();
expect(pointsBadge).toMatch(/\d+ taškai/);

// Check adventure map exists
const mapExists = await page.locator('.adventure-map').isVisible();
expect(mapExists).toBe(true);

// Check chores section
const choresExist = await page.locator('text=🧹 Darbai').isVisible();
expect(choresExist).toBe(true);

// Check rewards section
const rewardsExist = await page.locator('text=🎁 Apdovanojimai').isVisible();
expect(rewardsExist).toBe(true);

// Full page screenshot
await page.screenshot({ path: 'test-results/kid-home-elija.png', fullPage: true });
```

### Task 2.5: Chore Completion Testing

Test submitting chores for approval:

```
1. Login as Elija
2. Find a chore (e.g., "📬 Atnešti paštą")
3. Click "✅ Pateikti" button
4. Verify success message appears
5. Verify chore moves to "Laukiantys darbai" section
6. Verify status shows "⌛ Laukia patvirtinimo"
7. Test duplicate submission prevention (should show error)
```

**Expected Results**:
- Success message: "Pateikta patvirtinimui: [chore name]"
- Chore appears in pending section
- Duplicate submission blocked

**Test Script**:
```javascript
await page.goto('http://127.0.0.1:8000/kid/home/');

// Get initial points
const initialPoints = await getPointsBalance(page);

// Find and submit a chore
const choreCard = await page.locator('text=📬 Atnešti paštą').locator('..');
await choreCard.locator('button:has-text("✅ Pateikti")').click();

// Wait for redirect and check success message
await page.waitForURL('**/kid/home/');
const message = await page.locator('.alert-success, .messages').textContent();
expect(message).toContain('Pateikta patvirtinimui');

// Verify in pending section
const pendingSection = await page.locator('text=⌛ Laukiantys darbai');
expect(await pendingSection.isVisible()).toBe(true);

// Test duplicate prevention
await choreCard.locator('text=⌛ Laukia patvirtinimo').isVisible();
// Try to submit again - button should not be available or show pending state
```

### Task 2.6: Reward Redemption Testing

Test requesting rewards:

```
1. Login as kid with sufficient points
2. Find an affordable reward
3. Click "🎯 Prašyti" button
4. Verify request appears in pending redemptions
5. Test insufficient points scenario (should block or warn)
```

**Expected Results**:
- Request created successfully
- Appears in "Laukiantys apdovanojimai"
- Points not deducted until approved

**Test Script**:
```javascript
await page.goto('http://127.0.0.1:8000/kid/home/');

// Find affordable reward
const points = await getPointsBalance(page);
const rewardCard = await page.locator('.reward-item').first();
const rewardCost = parseInt(await rewardCard.locator('.cost').textContent());

if (points >= rewardCost) {
    await rewardCard.locator('button:has-text("🎯 Prašyti")').click();
    await page.waitForURL('**/kid/home/');
    
    // Verify in pending
    const pendingRedemptions = await page.locator('text=⌛ Laukiantys apdovanojimai');
    expect(await pendingRedemptions.isVisible()).toBe(true);
}
```

### Task 2.7: PIN Change Flow Testing

Test PIN change functionality:

```
1. Login as Elija (PIN: 1234)
2. Click "🔐 Keisti PIN" button
3. Test scenarios:
   a. Valid: Old PIN correct, new PIN matches confirmation
   b. Invalid old PIN: Should show error
   c. Mismatched confirmation: Should show error
   d. Too short PIN (<4 chars): Should show error
4. After successful change, logout and login with new PIN
5. Change PIN back to original
```

**Expected Results**:
- Successful change shows success message
- Old PIN verified before change
- Confirmation matching enforced
- New PIN works for login

**Test Script**:
```javascript
// Test valid PIN change
await page.goto('http://127.0.0.1:8000/kid/home/');
await page.click('a:has-text("🔐 Keisti PIN")');
await page.waitForURL('**/kid/change-pin/');

// Fill form
await page.fill('#id_old_pin', '1234');
await page.fill('#id_new_pin', '9999');
await page.fill('#id_confirm_pin', '9999');
await page.click('button:has-text("✅ Pakeisti PIN")');

// Check success
await page.waitForURL('**/kid/home/');
expect(await page.textContent('body')).toContain('PIN sėkmingai pakeistas');

// Test login with new PIN
await page.goto('http://127.0.0.1:8000/kid/logout/');
await page.goto('http://127.0.0.1:8000/kid/login/');
await page.click('[alt="Elija"]');
// Enter 9999
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("9")');
await page.click('button:has-text("✓ Prisijungti")');
await page.waitForURL('**/kid/home/');

// Change back to 1234
// ... (repeat process)
```

### Task 2.8: Admin Panel Testing

Test Django admin functionality:

```
1. Navigate to /admin/
2. Login with superuser credentials
3. Test CRUD operations:
   - Create new Kid
   - Edit existing Chore
   - Delete test Reward
   - Approve pending ChoreLog
   - Reject pending Redemption
4. Test bulk actions:
   - Select multiple ChoreLog entries
   - Bulk approve
   - Verify points updated correctly
5. Test admin actions for point adjustments
```

**Expected Results**:
- All CRUD operations work
- Bulk approve updates points atomically
- Admin UI displays Lithuanian text for actions

**Test Script**:
```javascript
await page.goto('http://127.0.0.1:8000/admin/');
await page.fill('#id_username', 'admin');
await page.fill('#id_password', 'your_admin_password');
await page.click('input[type="submit"]');
await page.waitForURL('**/admin/');

// Navigate to ChoreLog
await page.click('a:has-text("Chore logs")');

// Select pending entries
await page.check('input[name="_selected_action"]:first-of-type');
await page.check('input[name="_selected_action"]:nth-of-type(2)');

// Bulk approve
await page.selectOption('select[name="action"]', 'approve_pending_logs');
await page.click('button:has-text("Go")');

// Confirm action
await page.click('input[type="submit"]');

// Verify success message
expect(await page.textContent('body')).toContain('patvirtinta');
```

### Task 2.9: Adventure Map Testing

Test milestone progression:

```
1. Login as kid
2. Verify map displays correctly
3. Check milestone states:
   - Completed milestones (green checkmark)
   - Current milestone (glowing)
   - Future milestones (locked)
4. Test map theme changes (if feature exists)
5. Verify confetti animation on new achievements
```

**Expected Result**: Map renders with correct milestone states

**Test Script**:
```javascript
await page.goto('http://127.0.0.1:8000/kid/home/');

// Check map exists
const mapVisible = await page.locator('.adventure-map').isVisible();
expect(mapVisible).toBe(true);

// Count milestones
const milestones = await page.locator('.milestone').count();
expect(milestones).toBeGreaterThan(0);

// Check for completed milestones
const completedMilestones = await page.locator('.milestone.completed').count();
console.log(`Completed milestones: ${completedMilestones}`);

// Check current milestone glows
const currentMilestone = await page.locator('.milestone.current');
expect(await currentMilestone.isVisible()).toBe(true);

// Screenshot map
await page.locator('.adventure-map').screenshot({ path: 'test-results/adventure-map.png' });
```

### Task 2.10: Mobile Responsiveness Testing

Test mobile browser behavior:

```
1. Resize browser to mobile dimensions (375x667)
2. Test all pages at mobile size
3. Verify touch-friendly buttons
4. Test mobile navigation
5. Check image scaling
6. Test PIN entry on mobile
```

**Expected Result**: App is fully functional on mobile viewport

**Test Script**:
```javascript
// Set mobile viewport
await page.setViewportSize({ width: 375, height: 667 });

// Test landing page
await page.goto('http://127.0.0.1:8000/');
await page.screenshot({ path: 'test-results/mobile-landing.png', fullPage: true });

// Test kid login
await page.goto('http://127.0.0.1:8000/kid/login/');
await page.screenshot({ path: 'test-results/mobile-login.png', fullPage: true });

// Test kid home
await loginAsElija(page);
await page.screenshot({ path: 'test-results/mobile-home.png', fullPage: true });

// Verify elements are visible and clickable
const choreButtons = await page.locator('button:has-text("✅ Pateikti")').all();
for (const button of choreButtons.slice(0, 3)) {
    expect(await button.isVisible()).toBe(true);
}
```

## Phase 3: Unit Testing with Django Test Framework

### Task 3.1: Create Model Tests

Create `chorepoints/core/tests/test_models.py`:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Kid, Chore, Reward, ChoreLog, Redemption, PointAdjustment
from django.utils import timezone

class KidModelTests(TestCase):
    
    def setUp(self):
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
    
    def test_kid_creation(self):
        """Test Kid model creation"""
        self.assertEqual(self.kid.name, "Test Kid")
        self.assertEqual(self.kid.pin, "1234")
        self.assertEqual(self.kid.points_balance, 100)
        self.assertTrue(self.kid.active)
    
    def test_kid_str_method(self):
        """Test Kid __str__ method"""
        self.assertEqual(str(self.kid), "Test Kid")
    
    def test_kid_avatar_display(self):
        """Test Kid avatar display logic"""
        # With emoji
        self.kid.avatar_emoji = "😊"
        self.assertEqual(self.kid.get_avatar_display(), "😊")
        
        # Without emoji - should use monogram
        self.kid.avatar_emoji = ""
        self.assertIn("T", self.kid.get_avatar_display())
    
    def test_map_progress(self):
        """Test get_map_progress method"""
        progress = self.kid.get_map_progress()
        self.assertIn('milestones', progress)
        self.assertIn('progress_percentage', progress)
        self.assertIn('current_milestone', progress)
        self.assertIsInstance(progress['milestones'], list)
    
    def test_achievements(self):
        """Test get_achievements method"""
        achievements = self.kid.get_achievements()
        self.assertIsInstance(achievements, list)
        # Check each achievement has required fields
        for ach in achievements:
            self.assertIn('id', ach)
            self.assertIn('name', ach)
            self.assertIn('emoji', ach)
            self.assertIn('unlocked', ach)


class ChoreLogModelTests(TestCase):
    
    def setUp(self):
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=0
        )
        self.chore = Chore.objects.create(
            title="Test Chore",
            parent=self.parent,
            points=10
        )
    
    def test_chorelog_creation(self):
        """Test ChoreLog creation"""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=10
        )
        self.assertEqual(log.status, ChoreLog.Status.PENDING)
        self.assertEqual(log.points_awarded, 10)
        self.assertIsNone(log.processed_at)
    
    def test_chorelog_approve(self):
        """Test ChoreLog approval updates points"""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=10
        )
        
        # Initially 0 points
        self.assertEqual(self.kid.points_balance, 0)
        
        # Approve
        log.approve()
        
        # Refresh kid from database
        self.kid.refresh_from_db()
        
        # Should have 10 points now
        self.assertEqual(self.kid.points_balance, 10)
        self.assertEqual(log.status, ChoreLog.Status.APPROVED)
        self.assertIsNotNone(log.processed_at)
    
    def test_chorelog_reject(self):
        """Test ChoreLog rejection doesn't update points"""
        log = ChoreLog.objects.create(
            child=self.kid,
            chore=self.chore,
            points_awarded=10
        )
        
        # Reject
        log.reject()
        
        # Refresh kid from database
        self.kid.refresh_from_db()
        
        # Should still have 0 points
        self.assertEqual(self.kid.points_balance, 0)
        self.assertEqual(log.status, ChoreLog.Status.REJECTED)
        self.assertIsNotNone(log.processed_at)
    
    def test_bulk_approve_atomic(self):
        """Test bulk approval updates points correctly (no race condition)"""
        # Create multiple logs
        log1 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=10)
        log2 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=15)
        log3 = ChoreLog.objects.create(child=self.kid, chore=self.chore, points_awarded=20)
        
        # Approve all
        log1.approve()
        log2.approve()
        log3.approve()
        
        # Refresh kid
        self.kid.refresh_from_db()
        
        # Should have 45 points total
        self.assertEqual(self.kid.points_balance, 45)


class RedemptionModelTests(TestCase):
    
    def setUp(self):
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
        self.reward = Reward.objects.create(
            title="Test Reward",
            parent=self.parent,
            cost_points=50
        )
    
    def test_redemption_creation(self):
        """Test Redemption creation"""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=50
        )
        self.assertEqual(redemption.status, Redemption.Status.PENDING)
        self.assertEqual(redemption.cost_points, 50)
    
    def test_redemption_approve_deducts_points(self):
        """Test Redemption approval deducts points"""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=50
        )
        
        # Initially 100 points
        self.assertEqual(self.kid.points_balance, 100)
        
        # Approve
        redemption.approve()
        
        # Refresh kid
        self.kid.refresh_from_db()
        
        # Should have 50 points left
        self.assertEqual(self.kid.points_balance, 50)
        self.assertEqual(redemption.status, Redemption.Status.APPROVED)
    
    def test_redemption_reject_preserves_points(self):
        """Test Redemption rejection preserves points"""
        redemption = Redemption.objects.create(
            child=self.kid,
            reward=self.reward,
            cost_points=50
        )
        
        # Reject
        redemption.reject()
        
        # Refresh kid
        self.kid.refresh_from_db()
        
        # Should still have 100 points
        self.assertEqual(self.kid.points_balance, 100)
        self.assertEqual(redemption.status, Redemption.Status.REJECTED)


class PointAdjustmentModelTests(TestCase):
    
    def setUp(self):
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
    
    def test_point_adjustment_creation(self):
        """Test PointAdjustment creation updates balance"""
        adjustment = PointAdjustment.objects.create(
            child=self.kid,
            amount=25,
            reason="Bonus points",
            created_by=self.parent
        )
        
        # Refresh kid
        self.kid.refresh_from_db()
        
        # Should have 125 points now
        self.assertEqual(self.kid.points_balance, 125)
        self.assertEqual(adjustment.amount, 25)
    
    def test_negative_point_adjustment(self):
        """Test negative PointAdjustment (penalty)"""
        adjustment = PointAdjustment.objects.create(
            child=self.kid,
            amount=-20,
            reason="Penalty",
            created_by=self.parent
        )
        
        # Refresh kid
        self.kid.refresh_from_db()
        
        # Should have 80 points now
        self.assertEqual(self.kid.points_balance, 80)
```

### Task 3.2: Create View Tests

Create `chorepoints/core/tests/test_views.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import Kid, Chore, Reward, ChoreLog, Redemption

class KidLoginViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
    
    def test_kid_login_page_loads(self):
        """Test kid login page loads successfully"""
        response = self.client.get(reverse('kid_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kid')
    
    def test_kid_login_success(self):
        """Test successful kid login"""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('kid_home'))
        
        # Check session
        self.assertEqual(self.client.session.get('kid_id'), self.kid.id)
    
    def test_kid_login_invalid_pin(self):
        """Test kid login with invalid PIN"""
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '9999'
        })
        self.assertEqual(response.status_code, 200)  # Stays on page
        self.assertContains(response, 'Neteisingas PIN')
    
    def test_kid_login_inactive_kid(self):
        """Test kid login with inactive kid"""
        self.kid.active = False
        self.kid.save()
        
        response = self.client.post(reverse('kid_login'), {
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'neaktyvi')


class KidHomeViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
        self.chore = Chore.objects.create(
            title="Test Chore",
            parent=self.parent,
            points=10
        )
        self.reward = Reward.objects.create(
            title="Test Reward",
            parent=self.parent,
            cost_points=50
        )
    
    def login_kid(self):
        """Helper to login kid"""
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_kid_home_requires_login(self):
        """Test kid home redirects without login"""
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('kid_login'))
    
    def test_kid_home_loads_when_logged_in(self):
        """Test kid home loads with login"""
        self.login_kid()
        response = self.client.get(reverse('kid_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Kid')
        self.assertContains(response, '100 taškai')
    
    def test_kid_home_shows_chores(self):
        """Test kid home displays available chores"""
        self.login_kid()
        response = self.client.get(reverse('kid_home'))
        self.assertContains(response, 'Test Chore')
        self.assertContains(response, '10 tšk')
    
    def test_kid_home_shows_rewards(self):
        """Test kid home displays available rewards"""
        self.login_kid()
        response = self.client.get(reverse('kid_home'))
        self.assertContains(response, 'Test Reward')
        self.assertContains(response, '50 tšk')


class CompleteChoreViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=0
        )
        self.chore = Chore.objects.create(
            title="Test Chore",
            parent=self.parent,
            points=10
        )
    
    def login_kid(self):
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_complete_chore_requires_login(self):
        """Test chore completion requires login"""
        response = self.client.post(
            reverse('complete_chore', args=[self.chore.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('kid_login'))
    
    def test_complete_chore_creates_pending_log(self):
        """Test chore completion creates pending log"""
        self.login_kid()
        response = self.client.post(
            reverse('complete_chore', args=[self.chore.id])
        )
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check log created
        log = ChoreLog.objects.filter(child=self.kid, chore=self.chore).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, ChoreLog.Status.PENDING)
        self.assertEqual(log.points_awarded, 10)
        
        # Points not added yet (pending)
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.points_balance, 0)
    
    def test_complete_chore_duplicate_prevention(self):
        """Test duplicate chore submission prevention"""
        self.login_kid()
        
        # First submission
        self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        # Second submission
        response = self.client.post(reverse('complete_chore', args=[self.chore.id]))
        
        # Should show error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('laukia patvirtinimo' in str(m) for m in messages))
        
        # Should only have one log
        count = ChoreLog.objects.filter(child=self.kid, chore=self.chore).count()
        self.assertEqual(count, 1)


class ChangePinViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234",
            points_balance=100
        )
    
    def login_kid(self):
        session = self.client.session
        session['kid_id'] = self.kid.id
        session.save()
    
    def test_change_pin_page_requires_login(self):
        """Test change PIN page requires login"""
        response = self.client.get(reverse('change_pin'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('kid_login'))
    
    def test_change_pin_page_loads(self):
        """Test change PIN page loads"""
        self.login_kid()
        response = self.client.get(reverse('change_pin'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keisti PIN')
    
    def test_change_pin_success(self):
        """Test successful PIN change"""
        self.login_kid()
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check PIN changed
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '5678')
    
    def test_change_pin_wrong_old_pin(self):
        """Test PIN change with wrong old PIN"""
        self.login_kid()
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '9999',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        
        # Should stay on page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Neteisingas senas PIN')
        
        # PIN should not change
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '1234')
    
    def test_change_pin_mismatch_confirmation(self):
        """Test PIN change with mismatched confirmation"""
        self.login_kid()
        response = self.client.post(reverse('change_pin'), {
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5679'
        })
        
        # Should show validation error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nesutampa')
        
        # PIN should not change
        self.kid.refresh_from_db()
        self.assertEqual(self.kid.pin, '1234')
```

### Task 3.3: Create Form Tests

Create `chorepoints/core/tests/test_forms.py`:

```python
from django.test import TestCase
from django.contrib.auth.models import User
from core.forms import KidLoginForm, ChangePinForm
from core.models import Kid

class KidLoginFormTests(TestCase):
    
    def setUp(self):
        self.parent = User.objects.create_user('parent', 'parent@test.com', 'pass123')
        self.kid = Kid.objects.create(
            name="Test Kid",
            parent=self.parent,
            pin="1234"
        )
    
    def test_form_valid_data(self):
        """Test form with valid data"""
        form = KidLoginForm(data={
            'kid': self.kid.id,
            'pin': '1234'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_missing_kid(self):
        """Test form with missing kid"""
        form = KidLoginForm(data={
            'pin': '1234'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_missing_pin(self):
        """Test form with missing PIN"""
        form = KidLoginForm(data={
            'kid': self.kid.id
        })
        self.assertFalse(form.is_valid())


class ChangePinFormTests(TestCase):
    
    def test_form_valid_data(self):
        """Test form with valid data"""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5678'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_mismatched_pins(self):
        """Test form with mismatched new PIN and confirmation"""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '5678',
            'confirm_pin': '5679'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nesutampa', str(form.errors))
    
    def test_form_new_pin_too_short(self):
        """Test form with new PIN too short"""
        form = ChangePinForm(data={
            'old_pin': '1234',
            'new_pin': '56',
            'confirm_pin': '56'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_missing_fields(self):
        """Test form with missing required fields"""
        form = ChangePinForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # All three fields required
```

### Task 3.4: Run All Unit Tests

Execute the test suite:

```bash
cd chorepoints
python manage.py test core.tests
```

**Expected Result**: All tests pass

**If tests fail**:
1. Read error messages carefully
2. Fix the code or update tests
3. Re-run until all pass

**Generate Coverage Report** (optional):

```bash
pip install coverage
coverage run --source='core' manage.py test core.tests
coverage report
coverage html
# Open htmlcov/index.html in browser
```

**Target**: >80% code coverage

## Phase 4: Integration Testing

### Task 4.1: End-to-End User Flow Test

Test complete user journey:

```
1. Parent creates new kid in admin
2. Kid logs in for first time
3. Kid completes chore
4. Parent approves in admin
5. Kid sees updated points and confetti
6. Kid requests reward
7. Parent approves reward
8. Kid sees reduced points
9. Kid changes PIN
10. Kid logs out and back in with new PIN
```

**Expected Result**: Complete flow works seamlessly

### Task 4.2: Concurrent User Testing

Test multiple kids simultaneously:

```
1. Open two browser windows
2. Login as different kids in each
3. Submit chores from both
4. Approve both in admin
5. Verify both kids' points update correctly
6. Check for race conditions
```

**Expected Result**: No data corruption, all updates atomic

### Task 4.3: Data Integrity Testing

Test database constraints:

```
1. Try to create kid with duplicate name (should allow)
2. Try to delete parent with kids (should cascade or prevent)
3. Try to approve already-approved ChoreLog (should prevent)
4. Try to redeem reward with insufficient points (should prevent in UI)
5. Test negative point balances (should handle gracefully)
```

**Expected Result**: Data remains consistent

## Phase 5: Security Testing

### Task 5.1: Authentication Testing

```
1. Try accessing /kid/home/ without login → Should redirect
2. Try accessing another kid's session → Should fail
3. Try SQL injection in PIN field → Should be safe
4. Try XSS in kid name → Should be escaped
5. Test CSRF protection on forms → Should require token
```

**Expected Result**: All unauthorized access blocked

### Task 5.2: Authorization Testing

```
1. Try admin panel without authentication → Should redirect to login
2. Try modifying another parent's chores → Should fail
3. Test kid can't access admin functions → Should fail
4. Test kid can only see own data → Should pass
```

**Expected Result**: Proper authorization enforced

## Phase 6: Performance Testing

### Task 6.1: Query Optimization

Use Django Debug Toolbar or query logging:

```python
from django.db import connection
from django.test.utils import override_settings

# Test queries on kid home page
with self.assertNumQueries(10):  # Adjust expected number
    response = self.client.get(reverse('kid_home'))
```

**Expected Result**: No N+1 queries, minimal database hits

### Task 6.2: Load Time Testing

Measure page load times:

```javascript
await page.goto('http://127.0.0.1:8000/kid/home/');
const performanceTiming = JSON.parse(
    await page.evaluate(() => JSON.stringify(window.performance.timing))
);

const loadTime = performanceTiming.loadEventEnd - performanceTiming.navigationStart;
console.log(`Page load time: ${loadTime}ms`);
expect(loadTime).toBeLessThan(3000);  // Should load in under 3 seconds
```

**Expected Result**: Pages load in <3 seconds

## Phase 7: Error Handling Testing

### Task 7.1: Test Error Pages

```
1. Navigate to non-existent URL → Should show 404
2. Trigger 500 error (if possible) → Should show error page
3. Test with DEBUG=False → Should show user-friendly errors
```

**Expected Result**: Graceful error handling

### Task 7.2: Test Edge Cases

```
1. Submit chore for non-existent chore ID → Should handle gracefully
2. Login with extremely long PIN → Should validate
3. Upload very large image as avatar → Should handle or reject
4. Test with 0 points balance → Should display correctly
5. Test with negative points → Should handle
```

**Expected Result**: No crashes, appropriate error messages

## Phase 8: Documentation Testing

### Task 8.1: Verify README Instructions

Follow README.md step-by-step on fresh clone:

```
1. Clone repository
2. Follow dev.ps1 instructions
3. Run server
4. Verify all setup steps work
```

**Expected Result**: Documentation is accurate

### Task 8.2: Verify Deployment Guide

Review AZURE_DEPLOYMENT_GUIDE.md for accuracy:

```
1. Check all Azure resource names are correct
2. Verify all commands are valid
3. Test cost calculations
4. Check for broken links or references
```

**Expected Result**: Guide is complete and accurate

## Phase 9: Reporting

### Task 9.1: Create Test Report

Generate comprehensive test report:

```markdown
# ChorePoints QA Test Report

## Date: [Current Date]
## Tester: [Your Name]
## Branch: testing/comprehensive-qa

## Summary
- Total Tests Run: X
- Passed: X
- Failed: X
- Code Coverage: X%

## Test Results by Category

### Unit Tests
- Model Tests: ✅ PASS / ❌ FAIL
- View Tests: ✅ PASS / ❌ FAIL
- Form Tests: ✅ PASS / ❌ FAIL

### Browser Automation Tests
- Landing Page: ✅ PASS
- Kid Login: ✅ PASS
- Chore Completion: ✅ PASS
- [etc...]

### Security Tests
- Authentication: ✅ PASS
- Authorization: ✅ PASS
- [etc...]

## Issues Found
1. [Issue description] - Priority: HIGH/MEDIUM/LOW
2. [Issue description] - Priority: HIGH/MEDIUM/LOW

## Recommendations
1. [Recommendation]
2. [Recommendation]

## Screenshots
[Attach screenshots from test-results/ folder]

## Next Steps
[What needs to be fixed/improved]
```

### Task 9.2: Create Test Results Directory

Store all test artifacts:

```
test-results/
├── screenshots/
│   ├── landing-page.png
│   ├── kid-login.png
│   ├── kid-home-elija.png
│   └── [other screenshots]
├── coverage/
│   └── htmlcov/
├── test-report.md
└── playwright-report/
```

## Success Criteria

The QA testing is considered complete when:

- [ ] All unit tests pass (100%)
- [ ] All browser automation tests pass
- [ ] Code coverage >80%
- [ ] No critical bugs found
- [ ] Security tests pass
- [ ] Performance benchmarks met
- [ ] Documentation verified
- [ ] Test report generated
- [ ] All files committed to `testing/comprehensive-qa` branch

## Deliverables

1. **Test Suite**: Complete unit tests in `core/tests/`
2. **Test Report**: `test-results/test-report.md`
3. **Screenshots**: All test screenshots in `test-results/screenshots/`
4. **Coverage Report**: HTML coverage report in `test-results/coverage/`
5. **Bug List**: Any issues found documented
6. **Fixed Code**: Any bugs fixed and committed

## Notes

- Use `git commit` frequently with descriptive messages
- Create separate commits for:
  - Test file creation
  - Bug fixes
  - Documentation updates
- Push branch to remote when complete: `git push origin testing/comprehensive-qa`
- Create pull request for review

## Questions or Issues?

If you encounter issues during testing:

1. Check the existing documentation
2. Review error logs in console/terminal
3. Use Django Debug Toolbar for query analysis
4. Document the issue in test report
5. Attempt to fix and document the fix

Good luck with testing! 🧪🚀
