---
description: Close current issue by committing, creating PR, and merging (skips build by default)
---

Close the current issue by executing the complete workflow:
1. Commit all changes
2. Push to remote
3. Create pull request
4. Merge PR and delete branch
5. Switch to main and sync
6. Close the issue

**Default behavior: Skips the build step for speed**

Expected user input formats:
- `/issue-close` - Skip build, auto-generate commit message
- `/issue-close build` - Run ./scripts/build-all.sh before committing
- `/issue-close --build` - Run ./scripts/build-all.sh before committing
- `/issue-close "Custom commit message"` - Skip build, use custom message
- `/issue-close build "Custom commit message"` - Run build with custom message

The script will:
- Extract issue number from current branch name (format: `<num>-slug`)
- If no issue number found, it will error

Execution logic:
```bash
# Default (skip build):
bash scripts/issue-close.sh --skip-build [-m "<message>"]

# With build:
bash scripts/issue-close.sh [-m "<message>"]
```

After successful execution:
1. Changes will be committed (with custom or auto-generated message)
2. Branch will be pushed
3. PR will be created and merged
4. You will be switched to main branch
5. Issue will be closed
6. Feature branch will be deleted
7. Report the issue number, PR number, and completion status to the user
