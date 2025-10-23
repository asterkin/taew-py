---
description: Close current issue by committing, creating PR, and merging (skips build by default)
---

Close the current issue by executing the complete workflow:
1. Bump version based on issue label
2. Commit all changes
3. Push to remote
4. Create pull request
5. Merge PR and delete branch
6. Switch to main and sync
7. Close the issue

**Default behavior: Skips the build step for speed**

Expected user input formats:
- `/issue-close` - Skip build, auto-generate commit message, auto-bump version
- `/issue-close build` - Activate venv and run `make` (static checks + tests) before committing
- `/issue-close --build` - Activate venv and run `make` (static checks + tests) before committing
- `/issue-close "Custom commit message"` - Skip build, use custom message
- `/issue-close build "Custom commit message"` - Activate venv, run build with custom message
- `/issue-close --major` - Bump major version (X.0.0)
- `/issue-close --no-bump` - Skip version bump entirely

**Version Bumping:**
The script automatically determines version bump type from issue label:
- `enhancement` label → **minor** bump (2.1.1 → 2.2.0) - new features, non-breaking changes
- `bug` label → **patch** bump (2.1.1 → 2.1.2) - bug fixes, backwards compatible
- `documentation` label → **no bump** - documentation only changes
- `--major` flag → **major** bump (2.1.1 → 3.0.0) - breaking changes (overrides label)
- `--no-bump` flag → **no bump** - skip version update (overrides label)

Version is updated in both:
- `pyproject.toml` (project.version)
- `taew/__init__.py` (__version__)

The script will:
- Extract issue number from current branch name (format: `<num>-slug`)
- Fetch issue labels from GitHub to determine version bump
- Update version numbers before committing
- If no issue number found, it will error

Execution logic:
```bash
# Default (skip build, auto-bump):
bash scripts/issue-close.sh --skip-build [-m "<message>"] [--major | --no-bump]

# With build:
bash scripts/issue-close.sh [-m "<message>"] [--major | --no-bump]
```

After successful execution:
1. Version will be bumped (if applicable)
2. Changes will be committed (with custom or auto-generated message)
3. Branch will be pushed
4. PR will be created and merged
5. You will be switched to main branch
6. Issue will be closed
7. Feature branch will be deleted
8. Report the issue number, PR number, version change, and completion status to the user
