---
applyTo: '**'
---

# 🎨 ChorePoints Kid UI Enhancement - Active Development Guide

**Branch:** `feature/kid-ui-enhancement`  
**Started:** October 25, 2025  
**Last Updated:** October 25, 2025 (**Phase 2.1 COMPLETE** - Loading states with spinner overlay)

> **IMPORTANT:** This file tracks ongoing UI enhancement work. Update completion status after each task and commit changes to track progress.

---

## 📊 OVERALL PROGRESS TRACKER

```
Phase 1: Core Visual Improvements    [████████████████████] 100% ✅ COMPLETE
Phase 2: Micro-Interactions           [████████████████████] 100% ✅ COMPLETE
Phase 3: Typography & Content         [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ PENDING
Phase 4: Advanced Features            [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ PENDING
Phase 5: Accessibility & Performance  [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ PENDING
```

**Overall Completion:** 52% (Phases 1 & 2 complete)

---

## ✅ PHASE 1: CORE VISUAL IMPROVEMENTS - COMPLETE

### 1.1 Enhanced Color Palette & Gradients ✅
- [x] **Completed:** October 25, 2025
- [x] Base colors implemented with CSS custom properties
- [x] Gradient definitions added (warm, cool, success, rainbow)
- [x] Dark mode variables prepared (not activated yet)
- **Files Modified:** `chorepoints/core/templates/base.html`
- **Commit:** Included in Phase 1 commit

### 1.2 Card Design Overhaul ✅
- [x] **Completed:** October 25, 2025
- [x] 3D hover tilt effects with `transform: perspective()`
- [x] Gradient backgrounds for card types
- [x] Pulse animations for available items
- [x] Shine effect on hover using `::before` pseudo-element
- [x] Icon badges with 2.5rem emojis
- [x] Corner ribbons CSS prepared (not activated on all cards yet)
- **Files Modified:** `chorepoints/core/templates/base.html`
- **CSS Classes Added:** `.kid-card`, `.kid-card-shine`, `.kid-card-hover`

### 1.3 Button Enhancements ✅
- [x] **Completed:** October 25, 2025
- [x] Ripple effect on click (JavaScript-based)
- [x] Bounce animation on hover (`@keyframes btnBounce`)
- [x] Color transitions (300ms ease)
- [x] Icon animations prepared
- [x] Disabled state styling with opacity and cursor
- **Files Modified:** `chorepoints/core/templates/base.html`
- **CSS Classes Added:** `.kid-btn`, `.kid-btn-primary`, `.kid-btn-success`, `.kid-btn-ripple`
- **JavaScript Added:** `createRipple()` function

### 1.4 Typography Foundation ✅
- [x] **Completed:** October 25, 2025
- [x] Google Font "Fredoka" imported and applied
- [x] Font sizes increased for kid-facing content
- [x] Line-height improved (1.6 for body)
- **Files Modified:** `chorepoints/core/templates/base.html`

---

## 🚧 PHASE 2: MICRO-INTERACTIONS & ANIMATIONS - IN PROGRESS

### 2.1 Chore Submission Feedback ✅
**Priority:** HIGH | **Status:** COMPLETED | **Completed:** October 25, 2025

#### Tasks:
- [x] **Toast Notification System** ✅
  - [x] Create toast container HTML structure
  - [x] Implement `showToast(message, type)` JavaScript function
  - [x] Add CSS for toast slide-in animation
  - [x] Integrate with Django messages framework
  - [x] Test success, error, and info variants
  - **Target File:** `chorepoints/core/templates/kid/home.html` ✅
  - **Also Modified:** `chorepoints/core/views.py` ✅
  
- [x] **Point Counter Animation** ✅
  - [x] Add `animatePointChange(oldValue, newValue)` function
  - [x] Store previous point value in session or data attribute
  - [x] Trigger animation on page load when points changed
  - [x] Add pulse effect to point badge during animation
  - **Target File:** `chorepoints/core/templates/kid/home.html` ✅
  - **Also Modified:** `chorepoints/core/views.py` ✅
  
- [x] **Enhanced Confetti Effect** ✅
  - [x] Increase particle count (160 → 200) ✅
  - [x] Add shape variety (circles, squares, stars) ✅
  - [x] Improve color distribution (10 vibrant colors) ✅
  - [x] Add rotation animation for all shapes ✅
  - [x] Add opacity fade-out effect ✅
  - [x] Longer animation duration (320 → 380 frames) ✅
  - [ ] Add optional sound effect trigger point (audio element) - Deferred
  - **Target File:** `chorepoints/core/templates/kid/home.html` ✅

- [x] **Loading States** ✅
  - [x] Add spinner overlay for form submissions ✅
  - [x] Disable button during async actions ✅
  - [x] Show progress indicator for longer operations ✅
  - [x] Prevent double-submission with form state tracking ✅
  - [x] Handle back button navigation (pageshow event) ✅
  - **Target Files:** `kid/home.html` ✅

#### Implementation Notes (Toast Completed):
```javascript
// ✅ IMPLEMENTED: Toast notification system
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `kid-toast kid-toast-${type}`;
    
    const emojiMap = {
      success: '🎉',
      error: '❌',
      info: 'ℹ️'
    };
    
    toast.innerHTML = `
      <span class="toast-emoji">${emojiMap[type] || '✅'}</span>
      <span>${message}</span>
    `;
    
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('kid-toast-show'), 10);
    setTimeout(() => {
      toast.classList.remove('kid-toast-show');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ✅ IMPLEMENTED: Django messages integration
(function() {
  const messages = {{ django_messages_json|safe|default:"[]" }};
  messages.forEach((msg, index) => {
    setTimeout(() => {
      showToast(msg.message, msg.level);
    }, index * 150); // Stagger multiple messages
  });
})();
```

**Django view integration:**
- Added `django_messages_json` context variable to `kid_home()` view
- Converts Django messages to JSON format with level mapping
- SUCCESS → 'success', ERROR → 'error', INFO/WARNING → 'info'

**Point Counter Animation (Completed):**
```javascript
// ✅ IMPLEMENTED: Point counter animation with counting effect
function animatePointChange(oldValue, newValue) {
    const badge = document.getElementById('points-badge');
    const valueSpan = document.getElementById('points-value');
    const duration = 1000; // 1 second
    const steps = 30;
    const increment = (newValue - oldValue) / steps;
    
    let current = oldValue;
    badge.classList.add('animating'); // Triggers scale and glow effect
    
    const interval = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= newValue) || (increment < 0 && current <= newValue)) {
            clearInterval(interval);
            valueSpan.textContent = newValue;
            setTimeout(() => badge.classList.remove('animating'), 300);
        } else {
            valueSpan.textContent = Math.round(current);
        }
    }, duration / steps);
}
```

**View changes:**
- Added `points_changed` boolean flag to detect point changes
- Added `old_points_balance` to track previous session value
- Modified `last_seen_balance` default to use current balance on first visit
- Animation triggers automatically on page load if points changed

**CSS additions:**
```css
.points-badge.animating {
    animation: pointsChange 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
@keyframes pointsChange {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); box-shadow: 0 8px 20px rgba(255, 152, 0, .8); }
    100% { transform: scale(1); }
}
```

#### Testing Checklist:
- [x] Toast container added to DOM ✅
- [x] CSS animations implemented (slide-in, bounce) ✅
- [x] Django messages converted to JSON ✅
- [x] Toast appears on page load for Django messages ✅
- [x] Point counter animation implemented ✅
- [x] Point badge scales and glows during animation ✅
- [x] Points count up/down smoothly over 1 second ✅
- [x] Test on chore submission (Playwright automated test) ✅
- [x] Test point animation after approval (23→24 points) ✅
- [x] Verify confetti still works with new features ✅
- [ ] Test on mobile viewport (375px)
- [ ] Verify respects `prefers-reduced-motion`

---

### 2.2 Adventure Map Enhancements ✅
**Priority:** HIGH | **Status:** COMPLETED | **Completed:** October 25, 2025

#### Tasks:
- [x] **Animated Path Trail** ✅
  - [x] Add SVG path with dashed stroke
  - [x] Implement `@keyframes dashOffset` animation
  - [x] Connect milestones with curved path
  - **Target File:** `chorepoints/core/templates/kid/home.html` ✅
  - **Implementation:** Used `.map-path:after` with repeating-linear-gradient and pathDashMove animation
  
- [x] **Hover Tooltips** ✅
  - [x] Quick preview without opening modal
  - [x] Show milestone name and required points
  - [x] Add arrow pointer to tooltip
  - [x] Color-coded status (green=achieved, orange=affordable, gray=locked)
  - **CSS Class:** `.milestone-tooltip` ✅
  - **Target File:** `chorepoints/core/templates/kid/home.html` ✅
  
- [ ] **Character Movement Animation** ⏳
  - [ ] Add smooth slide transition when `map_position` changes
  - [ ] Implement character sprite flip for direction
  - [ ] Add bounce effect on arrival at milestone
  - **CSS Class:** `.kid-map-character-moving`
  - **Note:** Deferred to later - requires session tracking of position changes
  
- [ ] **Milestone Unlock Effect** ⏳
  - [ ] Create exploding star animation
  - [ ] Add glow pulse on newly unlocked milestone
  - [ ] Trigger sound effect (if audio enabled)
  - **Target:** Current milestone in map
  - **Note:** Deferred to later - enhancement to existing sparkle system
  
- [ ] **Progress Bubble Enhancement** ⏳
  - [ ] More engaging fill animation
  - [ ] Add percentage text inside bubble
  - [ ] Pulse effect when close to next milestone (>80%)
  - **Note:** Deferred to later - nice-to-have feature

#### Implementation Notes (Completed):
```css
/* ✅ IMPLEMENTED: Animated dashed path trail */
.map-path:after {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 3px;
    background: repeating-linear-gradient(
        to right,
        transparent 0,
        transparent 10px,
        rgba(255, 255, 255, 0.3) 10px,
        rgba(255, 255, 255, 0.3) 20px
    );
    animation: pathDashMove 1.5s linear infinite;
    z-index: 0;
}

@keyframes pathDashMove {
    from { background-position: 0 0; }
    to { background-position: 20px 0; }
}

/* ✅ IMPLEMENTED: Milestone hover tooltip with arrow */
.milestone-tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-8px);
    background: white;
    padding: 8px 12px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    white-space: nowrap;
    font-size: 0.875rem;
    z-index: 20;
    border: 3px solid;
}

/* Arrow pointer */
.milestone-tooltip:after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 6px solid transparent;
    border-top-color: inherit;
}

/* Hover state */
.milestone:hover .milestone-tooltip {
    opacity: 1;
    transform: translateX(-50%) translateY(-16px);
}

/* Color variants */
.milestone.completed .milestone-tooltip { border-color: #4CAF50; }
.milestone.current .milestone-tooltip { border-color: #FF9800; }
.milestone.future .milestone-tooltip { border-color: #9e9e9e; }
```

**HTML structure:**
```html
<div class="milestone-tooltip">
  {{ milestone.reward_title }}
  <br>
  {% if milestone.position <= map_data.current_position %}
    <small style="color: #4CAF50;">✅ Pasiekta!</small>
  {% elif kid.points_balance >= milestone.position %}
    <small style="color: #FF9800;">🎯 Gali prašyti!</small>
  {% else %}
    <small style="color: #9e9e9e;">🔒 {{ milestone.position }} tšk reikia</small>
  {% endif %}
</div>
```

#### Testing Checklist:
- [x] CSS animations added (path dash, tooltip hover)
- [x] Tooltip HTML structure inserted in milestone loop
- [x] Color-coded status messages (Lithuanian)
- [ ] Visual testing on running server
- [ ] Tooltips don't interfere with clicks
- [ ] Progress bubble updates accurately
- [ ] Test on mobile viewport (375px)

---

### 2.3 Login Page Improvements ✅
**Priority:** MEDIUM | **Status:** COMPLETED | **Completed:** October 25, 2025

#### Tasks:
- [x] **PIN Dot Fill Animation** ✅
  - [x] Add enhanced bounce effect with `@keyframes pinDotFill`
  - [x] Color change from gray to orange with glow effect
  - [x] Scale transform (0 → 1.5 → 0.9 → 1) with color transitions
  - **Target File:** `chorepoints/core/templates/kid/login.html` ✅
  
- [x] **Kid Tile Selection Effects** ✅
  - [x] Glow effect on hover (box-shadow with orange pulsing)
  - [x] Scale transform (1 → 1.05) with elevation
  - [x] Added `tile-glow` animation (1.5s infinite)
  - **CSS Class:** `.kid-tile:hover`, `@keyframes tile-glow` ✅
  
- [x] **Error Shake Animation** ✅
  - [x] Enhanced `@keyframes shake` with cubic-bezier easing
  - [x] Trigger on wrong PIN submission
  - [x] Add red color flash to PIN dots with glow
  - [x] Clear PIN after shake completes (600ms delay)
  - **CSS Classes:** `.pin-display.error`, `@keyframes error-flash` ✅
  
- [x] **Success Transition** ✅
  - [x] Fade out login form (opacity 1 → 0)
  - [x] Scale up selected kid tile (1 → 1.3 → 1.5 with fade)
  - [x] Smooth redirect with loading indicator
  - [x] Green pulse animation for PIN dots
  - **CSS Classes:** `.success-transition`, `@keyframes fadeOutScale`, `@keyframes selectedKidZoom` ✅

#### Implementation Notes:
```css
/* ✅ IMPLEMENTED: Enhanced PIN dot fill with bounce and glow */
@keyframes dot-fill {
  0% {
    transform: scale(0);
    background: #e0e0e0;
  }
  50% {
    transform: scale(1.5);
    background: #ffa726;
    box-shadow: 0 0 20px rgba(255, 152, 0, 1);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
    background: #ff9800;
  }
}

/* ✅ IMPLEMENTED: Kid tile glow effect on hover */
@keyframes tile-glow {
  0%, 100% {
    box-shadow: 0 8px 20px -4px rgba(0, 0, 0, .25), 0 0 20px rgba(255, 152, 0, .3);
  }
  50% {
    box-shadow: 0 8px 20px -4px rgba(0, 0, 0, .25), 0 0 40px rgba(255, 152, 0, .6);
  }
}

/* ✅ IMPLEMENTED: Error shake with red flash */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

@keyframes error-flash {
  0%, 100% { 
    background: transparent;
    border-color: #ccc;
  }
  25%, 75% { 
    background: #ef5350;
    border-color: #ef5350;
    box-shadow: 0 0 20px rgba(239, 83, 80, .8);
  }
  50% {
    background: #f44336;
    border-color: #f44336;
    box-shadow: 0 0 30px rgba(244, 67, 54, 1);
  }
}

/* ✅ IMPLEMENTED: Success transition with fade and zoom */
@keyframes fadeOutScale {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.9);
  }
}

@keyframes selectedKidZoom {
  0% {
    transform: translateY(-4px) scale(1.08);
    opacity: 1;
  }
  50% {
    transform: translateY(-4px) scale(1.3);
    opacity: 1;
  }
  100% {
    transform: translateY(-4px) scale(1.5);
    opacity: 0;
  }
}
```

**JavaScript enhancements:**
```javascript
// ✅ IMPLEMENTED: Success transition trigger
submitBtn.addEventListener('click', () => {
  // ... validation ...
  pinDisplay.classList.add('success');
  
  // Add success transition to entire form
  const container = document.querySelector('.login-container');
  setTimeout(() => {
    container.classList.add('success-transition');
  }, 300);
  
  // Submit form after animations complete
  setTimeout(() => {
    form.submit();
  }, 800);
});

// ✅ IMPLEMENTED: Clear PIN after error shake
{% if form.errors %}
pinDisplay.classList.add('error');
setTimeout(() => {
  pinDisplay.classList.remove('error');
  // Clear PIN after error shake
  pinValue = '';
  updateDisplay();
}, 600);
{% endif %}
```

#### Testing Checklist:
- [x] PIN dots animate on each number entry with bounce
- [x] Kid tiles glow with pulsing orange shadow on hover
- [x] Error shake triggers on wrong PIN with red flash
- [x] PIN clears automatically after error shake
- [x] Success transition fades out form and zooms selected kid
- [ ] Visual testing on running server
- [ ] Mobile touch interactions work properly
- [ ] Keyboard navigation works (0-9, Enter, Backspace)

---

## ⏳ PHASE 3: TYPOGRAPHY & CONTENT - PENDING

### 3.1 Font Improvements
**Status:** NOT STARTED | **Effort:** 1 hour

- [ ] Verify Fredoka loads correctly on all pages
- [ ] Increase font sizes for kid-facing headings (2rem → 2.5rem)
- [ ] Adjust line-height for longer text blocks (1.6 → 1.8)
- [ ] Add font fallbacks for offline support

### 3.2 Icon & Emoji Consistency
**Status:** NOT STARTED | **Effort:** 1-2 hours

- [ ] Standardize emoji sizes (list: 2rem, headers: 3rem, avatars: 4rem)
- [ ] Add text-shadow to emojis for depth
- [ ] Implement emoji animations on hover (rotate, bounce, scale)
- [ ] Create emoji utility classes (`.emoji-sm`, `.emoji-md`, `.emoji-lg`)

---

## ⏳ PHASE 4: ADVANCED FEATURES - PENDING

### 4.1 Sound Effects (Optional)
**Status:** NOT STARTED | **Effort:** 2-3 hours

- [ ] Add audio element to base.html
- [ ] Implement sound toggle in settings
- [ ] Add sounds: button click, success chime, coin jingle, error beep
- [ ] Store sound preference in session
- [ ] Find/create royalty-free sound files

### 4.2 Theme System
**Status:** PARTIALLY STARTED | **Effort:** 3-4 hours

- [ ] Complete Island theme (already in models)
- [ ] Complete Space theme
- [ ] Complete Rainbow theme
- [ ] Add theme selector UI in kid profile
- [ ] Store theme preference in Kid model (already has `map_theme` field)
- [ ] Apply theme-specific CSS variables

### 4.3 Achievement Badges
**Status:** NOT STARTED | **Effort:** 4-5 hours

- [ ] Design badge data model (or use PointAdjustment for milestones)
- [ ] Create badge icons (emoji-based initially)
- [ ] Add badge unlock animation
- [ ] Create badge collection page
- [ ] Award badges for milestones (5 chores, 10 chores, 100 points, etc.)

---

## ⏳ PHASE 5: ACCESSIBILITY & PERFORMANCE - ONGOING

### 5.1 Accessibility
**Status:** PARTIAL | **Effort:** 2-3 hours

- [x] Reduced motion support implemented
- [ ] Add ARIA labels to all interactive elements
- [ ] Improve keyboard navigation (tab order)
- [ ] Add screen reader announcements for dynamic content
- [ ] Test with high contrast mode
- [ ] Ensure 4.5:1 color contrast ratio

### 5.2 Performance
**Status:** NOT STARTED | **Effort:** 2 hours

- [ ] Audit animation performance (Chrome DevTools)
- [ ] Optimize confetti canvas rendering
- [ ] Lazy load kid avatars
- [ ] Minimize JavaScript execution time
- [ ] Test on low-end devices
- [ ] Add `will-change` to frequently animated elements

---

## 🎯 IMMEDIATE NEXT STEPS (Priority Order)

1. **START HERE:** Phase 2.1 - Toast Notification System (30 min)
2. **THEN:** Phase 2.1 - Point Counter Animation (45 min)
3. **THEN:** Phase 2.1 - Enhanced Confetti (30 min)
4. **THEN:** Phase 2.3 - Login Page PIN Animation (45 min)
5. **THEN:** Phase 2.2 - Adventure Map Path Animation (1 hour)

**After completing 2-3 tasks:** Commit changes with message format:
```
Phase 2.1: Add toast notifications and point counter animation
- Implemented showToast() function with slide-in effect
- Added point counter animation with counting effect
- Enhanced confetti with more particles and colors
```

---

## 📁 KEY FILES TO MODIFY

### High Priority (Phase 2)
- `chorepoints/core/templates/kid/home.html` - Main kid dashboard
- `chorepoints/core/templates/kid/login.html` - PIN entry and kid selection
- `chorepoints/core/templates/base.html` - Shared CSS/JS (already enhanced)

### Medium Priority (Phase 3-4)
- `chorepoints/core/templates/index.html` - Homepage hero section
- `chorepoints/core/views.py` - Add session tracking for animations
- `chorepoints/core/models.py` - Badge model (if implementing achievements)

### Lower Priority (Phase 5)
- `chorepoints/core/admin.py` - Admin UI improvements (optional)
- `chorepoints/settings.py` - Performance settings

---

## 🛠️ DEVELOPMENT COMMANDS

### Start Development Server
```powershell
cd C:\Users\User\Documents\python_apps\django_kid_rewards\chorepoints
./dev.ps1  # Automated venv + runserver + browser
```

### Manual Start
```powershell
cd C:\Users\User\Documents\python_apps\django_kid_rewards
.\.venv\Scripts\python.exe .\chorepoints\manage.py runserver
```

### Check Git Status
```powershell
cd C:\Users\User\Documents\python_apps\django_kid_rewards
git status --short
```

### Commit Progress
```powershell
git add .
git commit -m "Phase X.Y: [Feature name] - [Brief description]"
```

---

## 🧪 TESTING STRATEGY

### After Each Task
1. Manual visual inspection in browser
2. Test on mobile viewport (375px)
3. Test with "Reduce motion" enabled
4. Check browser console for errors

### After Each Phase
1. Run through all kid workflows (login → submit chore → view approval)
2. Test on different browsers (Chrome, Firefox, Edge)
3. Validate accessibility with keyboard navigation
4. Check performance (no jank, smooth 60fps)

### Before Final Merge
1. Complete Playwright test suite (to be written)
2. Cross-browser testing
3. Mobile device testing (real devices)
4. User acceptance testing with kids

---

## 🎨 DESIGN SYSTEM REFERENCE

### Color Palette (CSS Custom Properties)
```css
--kid-primary: #FF9800;        /* Warm Orange */
--kid-primary-light: #FFB74D;
--kid-primary-dark: #F57C00;
--kid-success: #4CAF50;        /* Fresh Green */
--kid-info: #2196F3;           /* Sky Blue */
--kid-reward: #9C27B0;         /* Purple */
--gradient-warm: linear-gradient(135deg, #FFE0B2 0%, #FFCCBC 100%);
--gradient-rainbow: linear-gradient(90deg, #FF6B6B, #FFD93D, #6BCF7F, #4D96FF, #9D6CFF);
```

### Spacing Scale
- `--space-xs`: 0.25rem (4px)
- `--space-sm`: 0.5rem (8px)
- `--space-md`: 1rem (16px)
- `--space-lg`: 1.5rem (24px)
- `--space-xl`: 2rem (32px)

### Border Radius
- Small: 8px
- Medium: 12px
- Large: 16px
- Circle: 50%

### Animation Durations
- Fast: 150ms (hover feedback)
- Medium: 300ms (state changes)
- Slow: 500ms (page transitions)
- Very Slow: 1000ms (counting animations)

### Typography
- Font: 'Fredoka', sans-serif
- Headings: 2.5rem / 2rem / 1.5rem
- Body: 1rem (16px)
- Small: 0.875rem (14px)

---

## 💡 IMPLEMENTATION TIPS

### CSS Animation Best Practices
```css
/* ✅ GOOD: GPU-accelerated properties */
.element {
    transform: translateX(100px);
    opacity: 0.5;
    will-change: transform; /* Use sparingly */
}

/* ❌ BAD: Triggers layout recalculation */
.element {
    width: 100px;
    left: 50px;
    margin-top: 20px;
}
```

### JavaScript Performance
```javascript
// ✅ GOOD: Debounce expensive operations
let timeout;
window.addEventListener('resize', () => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
        // Expensive operation
    }, 250);
});

// ❌ BAD: Runs on every resize event
window.addEventListener('resize', () => {
    // Expensive operation
});
```

### Accessibility
```html
<!-- ✅ GOOD: Semantic HTML + ARIA -->
<button aria-label="Pateikti darbus" class="kid-btn">
    ✅ Pateikti
</button>

<!-- ❌ BAD: Div button without labels -->
<div onclick="submit()">Click</div>
```

---

## 📝 UPDATE INSTRUCTIONS

**After completing ANY task:**
1. Change `[ ]` to `[x]` in the task list above
2. Update the phase progress bar percentage
3. Add "Completed: [Date]" note
4. Update "Last Updated" at top of file
5. Commit this file along with code changes

**Example commit:**
```
Phase 2.1: Add toast notifications (Task 1/4 complete)
- Implemented showToast() function in kid/home.html
- Added CSS animations for slide-in effect
- Updated ui-enhancment.md.instructions.md progress tracker
```

---

## 🆘 TROUBLESHOOTING

### Server Won't Start
```powershell
# Check if port 8000 is in use
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess

# Kill process and restart
taskkill /F /PID <process_id>
```

### Migrations Not Applying
```powershell
# Check migration status
.\.venv\Scripts\python.exe .\chorepoints\manage.py showmigrations core

# Reapply specific migration
.\.venv\Scripts\python.exe .\chorepoints\manage.py migrate core 0008
```

### CSS Not Updating
- Hard refresh: Ctrl+Shift+R
- Clear Django cache (DEBUG=True should auto-reload)
- Check for typos in CSS selectors
- Inspect element in DevTools to verify styles applied

---

## 📞 QUESTIONS FOR NEXT SESSION

When resuming work with a new AI agent, ask:

1. ✅ "Review the progress tracker in `.github/instructions/ui-enhancment.md.instructions.md` - what's the current completion status?"
2. ✅ "Should I start with Phase 2.1 toast notifications, or is there a different priority?"
3. ❓ "Do you want sound effects included in Phase 2, or skip audio for now?"
4. ❓ "Should confetti use the existing canvas approach or switch to CSS animations?"
5. ❓ "Are there any issues with Phase 1 animations that need fixing before continuing?"

---

## 🔗 RELATED DOCUMENTATION

- **Project Architecture:** `.github/copilot-instructions.md`
- **Adventure Map Spec:** `ADVENTURE_MAP_IMPLEMENTATION.md`
- **Full Enhancement Plan:** `UI_ENHANCEMENT_PLAN.md`
- **Validation Report:** `chorepoints/VALIDATION_REPORT.md`

---

**🎯 REMEMBER:** Update this file after EVERY task completion to track progress accurately!

**Last Sync:** Phase 1 complete, Phase 2 ready to start