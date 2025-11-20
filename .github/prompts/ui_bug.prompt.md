---
agent: agent
---
# 🐛 Fix Progress Map Milestone Bug

A visual bug exists in the **Nuotykių Žemėlapis** progress map.  
Use the screenshot for reference:  
`Screenshot 2025-11-20 140516.jpg`

## 🎯 What’s Wrong (Summary)
- Avatar is displayed on the **1000 taškų** milestone even though the user only has **409 taškų**.
- The **500 taškų** milestone is highlighted, but the avatar is not placed there.
- Tooltip “Dar 91 tšk!” correctly calculates the difference to 500, but it is positioned on the wrong milestone.
- Visual state of milestones (highlighting, filled/empty circles) does not match current progress.

## ✅ Expected Behavior
- Avatar should appear on **the milestone representing the user’s current tier**, not the next tier.
- Tooltip should point to **the next milestone** (500 taškų), but **avatar remains on the current tier** (between 300–500).
- Milestones should highlight only the **current** and **next** steps correctly.
- All milestone CSS states must match the real progress data.

## 🛠️ Tasks for Copilot
1. **Fix logic** that determines:
   - current milestone index  
   - next milestone index  
   - avatar placement container  
2. Ensure avatar is rendered inside **current** milestone element.
3. Ensure highlight styling applies to the correct milestones only.
4. Ensure tooltip points to the **next** milestone, not the avatar's milestone.
5. Review CSS/flex/absolute positioning to prevent avatar snapping to the wrong container.

## ✔️ Acceptance Criteria
- Avatar is always displayed on the correct milestone based on user's points.
- Tooltip always points to the upcoming milestone.
- No overlapping or misplaced elements.
- Works correctly on various point values (0–3000).
- No regression in mobile/desktop layout.

## 🧪 Optional (If Quick)
Add a small unit or UI test verifying correct milestone selection for:
- 0 pts  
- 49 pts  
- 300 pts  
- 409 pts  
- 500–999 pts  

##use atlasian MCP to login to prod as elija to confirm its fixed

