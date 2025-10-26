# Copilot Instructions for QA Testing

This directory contains instructions and progress tracking for comprehensive QA testing of the ChorePoints application.

## Files

### 📘 `comprehensive-qa-testing.md`
**Purpose**: Complete testing instructions and procedures  
**Use**: Reference this file for detailed testing steps, expected results, and test scripts

**Contains**:
- 9 testing phases with 35+ tasks
- MCP Pylance code analysis instructions
- MCP Playwright browser automation scripts
- Django unit test templates
- Security, performance, and integration testing procedures
- Test report template

### 📊 `qa-progress-tracker.md`
**Purpose**: Checkpoint system for tracking testing progress  
**Use**: Update this file as you complete tasks to enable resumption after interruptions

**Contains**:
- Phase-by-phase completion checkboxes
- Bug tracker with priority levels
- Session log for chronological progress
- Current checkpoint marker
- Statistics dashboard
- Quick command reference

## How to Use

### Starting a New QA Session

1. **Open the tracker**:
   ```powershell
   code .github/copilot-instructions/qa-progress-tracker.md
   ```

2. **Check current checkpoint**:
   - Look at "Current Checkpoint" section
   - Note the "Next Task" to resume

3. **Open testing instructions**:
   ```powershell
   code .github/copilot-instructions/comprehensive-qa-testing.md
   ```

4. **Navigate to current phase**:
   - Find the phase in the instructions
   - Read the task details
   - Execute the test

5. **Update progress**:
   - Mark task complete: `- [x]`
   - Add notes and findings
   - Document any bugs
   - Update checkpoint
   - Commit changes

### After a Chat Crash

**Recovery Process**:

1. **Reopen progress tracker**:
   ```powershell
   code .github/copilot-instructions/qa-progress-tracker.md
   ```

2. **Tell the new chat session**:
   > "I'm continuing QA testing from a previous session. Please read `.github/copilot-instructions/qa-progress-tracker.md` to see what's been completed, then read `.github/copilot-instructions/comprehensive-qa-testing.md` for instructions. Continue from the checkpoint marked in the tracker."

3. **The AI will**:
   - Read the progress tracker
   - Identify the last completed task
   - Resume from the next task
   - Continue updating the tracker

### Workflow Loop

```
┌─────────────────────────────────────────┐
│  1. Check qa-progress-tracker.md       │
│     - Find current checkpoint           │
│     - Note next task                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  2. Read comprehensive-qa-testing.md    │
│     - Find task instructions            │
│     - Review expected results           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  3. Execute the test                    │
│     - Run code/commands                 │
│     - Observe results                   │
│     - Take screenshots                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  4. Update qa-progress-tracker.md       │
│     - Mark task complete                │
│     - Document findings                 │
│     - Update checkpoint                 │
│     - Add bugs if found                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  5. Commit changes                      │
│     git add .                           │
│     git commit -m "QA: Complete X.Y"    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  6. Repeat for next task                │
│     (or take break - progress saved!)   │
└─────────────────────────────────────────┘
```

## Example Session

### Session Start
```
Human: "Continue QA testing from the progress tracker"

AI: [Reads qa-progress-tracker.md]
    - Last completed: Phase 1, Task 1.2
    - Next task: Phase 1, Task 1.3
    [Reads comprehensive-qa-testing.md]
    - Task 1.3: Check installed packages
    [Executes test...]
```

### After Completing Task
```
AI: [Updates qa-progress-tracker.md]
    - [x] Task 1.3: Check installed packages
    - Progress: 3/4 tasks
    - Notes: All packages installed correctly
    - Next Task: Phase 1, Task 1.4
    [Commits changes]
```

### Session Interrupted (Crash)
```
[Chat closes unexpectedly]
```

### New Session Resumes
```
Human: "I'm continuing QA testing. Read the progress tracker."

AI: [Reads qa-progress-tracker.md]
    - Last completed: Phase 1, Task 1.3
    - Current Checkpoint: Phase 1, Task 1.4
    - Resuming from: Run code snippet validation
    [Continues testing seamlessly]
```

## Tips for Success

### ✅ DO:
- Update tracker after EVERY completed task
- Commit frequently (at least after each task)
- Document bugs immediately when found
- Add detailed notes for complex issues
- Use checkboxes consistently
- Keep session log updated

### ❌ DON'T:
- Skip tracker updates (you'll lose progress)
- Work on multiple phases simultaneously
- Commit untested code
- Leave bugs undocumented
- Work directly on main branch
- Delete completed task notes

## Status Indicators

Use these in the tracker:

- `⏸️ NOT STARTED` - Phase hasn't begun yet
- `🔄 IN PROGRESS` - Currently working on this phase
- `✅ COMPLETED` - Phase done, all tasks passed
- `⚠️ BLOCKED` - Cannot proceed (missing dependency, etc.)
- `🔁 NEEDS RETRY` - Failed, requires another attempt

## Bug Priority Guide

When documenting bugs in tracker:

- **P0 (Critical)**: App crashes, data loss, security breach
- **P1 (High)**: Major feature broken, user cannot complete task
- **P2 (Medium)**: Minor feature issue, workaround exists
- **P3 (Low)**: Cosmetic issue, minor inconvenience

## Integration with GitHub Copilot

These instructions are designed to work with GitHub Copilot Chat. When you start a new chat:

1. Reference these files explicitly
2. Copilot will read and understand the context
3. It will continue from the checkpoint
4. It will maintain consistency across sessions

### Example Prompts:

**Starting fresh**:
> "Start QA testing by reading `.github/copilot-instructions/comprehensive-qa-testing.md` and tracking progress in `qa-progress-tracker.md`"

**Resuming**:
> "Continue QA testing from checkpoint in `qa-progress-tracker.md`"

**Checking status**:
> "Show me the current QA testing progress from the tracker"

**Fixing a bug**:
> "I found a bug during testing Phase 2, Task 2.5. Help me fix it and update the tracker."

## Success Metrics

By the end of QA testing:

- [ ] All 9 phases completed (35+ tasks)
- [ ] 100% of unit tests passing
- [ ] >80% code coverage
- [ ] All critical/high bugs fixed
- [ ] Test report generated
- [ ] Screenshots captured
- [ ] Branch ready for merge

---

**Version**: 1.0  
**Created**: 2025-10-26  
**Branch**: testing/comprehensive-qa  
**Maintainer**: QA Team
