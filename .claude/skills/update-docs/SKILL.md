---
name: update-docs
description: Update CHANGELOG.md and documentation files based on recent code changes (plan mode)
argument-hint: "[optional-context]"
allowed-tools: Read, Glob, Grep, Bash(git status*), Bash(git log*), Bash(git diff*)
---

# Update Documentation Command (Plan Mode)

Update project documentation based on recent code changes.

**User Context:** $ARGUMENTS

---

## PHASE 1: Analysis (Read-Only)

**IMPORTANT:** In this phase, only READ and ANALYZE. Do NOT make any changes yet.

### Step 1.1: Analyze Git State

Run these commands:

```bash
git status
git log --oneline -n 15
git diff --stat HEAD~5
```

### Step 1.2: Identify Changes

From the git output, identify:
- Files added/modified/deleted
- Features added or fixed
- Breaking changes
- Documentation gaps

### Step 1.3: Read Current Documentation

Read these files to understand current state:
- `CHANGELOG.md` - Current changelog entries
- `README.md` - Project readme
- `docs/` - Relevant documentation files

---

## PHASE 2: Present Plan

After analysis, present a **Documentation Update Plan** to the user:

```markdown
## Documentation Update Plan

### CHANGELOG.md Updates
- [ ] Add entry: "Added feature X" (under Added)
- [ ] Add entry: "Fixed bug Y" (under Fixed)
- [ ] ...

### Documentation Updates
- [ ] Update `docs/api/...` - Add new endpoint docs
- [ ] Update `README.md` - Update feature list
- [ ] ...

### Commit Plan
- Message: `docs: <summary of changes>`
- Files to stage: CHANGELOG.md, docs/..., README.md

### Questions (if any)
- Should X be documented under Added or Changed?
- ...
```

Then ask: **"Bu plan uygun mu? Onaylıyor musun?"** (Is this plan OK? Do you approve?)

---

## PHASE 3: Execute (After Approval Only)

**ONLY proceed after user explicitly approves the plan.**

### Step 3.1: Update CHANGELOG.md

1. If today's date section doesn't exist, create it
2. Add entries under appropriate headers:
   - **Added** - New features
   - **Fixed** - Bug fixes
   - **Changed** - Breaking changes or modifications
   - **Removed** - Removed features
   - **Documentation** - Doc-only changes
   - **Security** - Security fixes

### Step 3.2: Update Documentation Files

Update only the files identified in the plan.

### Step 3.3: Commit and Push

```bash
git add CHANGELOG.md docs/ README.md .claude/
git commit -m "docs: <planned message>

Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

---

## Important Notes

- **Phase 1-2:** Read-only analysis, no file modifications
- **Phase 3:** Only after explicit user approval
- Keep entries concise but informative
- Include file references for traceability
- Use conventional commit format (docs:, feat:, fix:, etc.)
- If uncommitted code changes exist, warn user first
