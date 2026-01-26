---
name: update-docs
description: Update CHANGELOG.md and documentation files based on recent code changes, then commit and push
disable-model-invocation: true
argument-hint: "[optional-context]"
---

# Update Documentation Command

Update project documentation based on recent code changes.

**User Context:** $ARGUMENTS

## Step 1: Analyze Recent Changes

Run these commands to understand what changed:

```bash
git status
git log --oneline -n 15
git diff --stat HEAD~5
```

Identify:
- What files were added/modified/deleted
- What features were added or fixed
- What breaking changes were made

## Step 2: Update CHANGELOG.md

Read the current CHANGELOG.md and add a new entry:

1. If today's date section doesn't exist, create it
2. Categorize changes under appropriate headers:
   - **Added** - New features
   - **Fixed** - Bug fixes
   - **Changed** - Breaking changes or modifications
   - **Removed** - Removed features
   - **Documentation** - Doc-only changes
   - **Security** - Security fixes

Format each entry with:
- Brief description
- File reference where relevant (e.g., `app/routers/auth.py`)

## Step 3: Update Related Documentation

Based on the changes, check and update:

| Change Type | Documentation to Update |
|-------------|------------------------|
| New API endpoint | `docs/api/` relevant file |
| Model changes | `docs/database/` files |
| Config changes | `docs/GETTING_STARTED.md` |
| New features | `README.md` |
| Architecture changes | `docs/architecture/` |
| Workflow changes | `docs/DEVELOPMENT_WORKFLOW.md` |

Only update files that are directly affected by the code changes.

## Step 4: Commit and Push

After all updates are complete:

1. Stage documentation changes:
   ```bash
   git add CHANGELOG.md docs/ README.md
   ```

2. Create commit with conventional message:
   ```bash
   git commit -m "docs: Update documentation based on recent changes

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

3. Push to remote:
   ```bash
   git push origin main
   ```

## Important Notes

- Always read existing CHANGELOG.md format before adding entries
- Keep entries concise but informative
- Include file references for traceability
- Use conventional commit format (docs:, feat:, fix:, etc.)
- If there are uncommitted code changes, warn the user and ask whether to include them
