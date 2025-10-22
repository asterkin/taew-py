---
description: Create a new GitHub issue with label, title, and optional body, then create and push a branch
---

Parse the user's request to extract:
- **label**: Issue type (bug, documentation, or enhancement)
- **title**: Issue title (may be quoted or unquoted)
- **body**: Optional issue description (may be quoted or unquoted)

Expected user input format:
```
/issue-new <label> "<title>" ["<body>"]
```

Examples:
- `/issue-new enhancement "Add Redis adapter" "Support pub/sub patterns"`
- `/issue-new bug "Fix serialization error" "Nested tuples fail to serialize"`
- `/issue-new documentation "Update API documentation"`

Execute the script:
```bash
bash scripts/issue-new.sh -l <label> -t "<title>" [-b "<body>"]
```

After successful execution:
1. A new GitHub issue will be created and assigned to @me
2. A new branch will be created with format: `<issue-number>-<slugified-title>`
3. The branch will be pushed to origin
4. You will be automatically switched to the new branch
5. Report the issue number, URL, and branch name to the user
