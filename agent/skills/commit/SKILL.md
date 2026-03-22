---
name: commit
description: Git commit best practices following Conventional Commits
---

# Git Commit Skill

## Overview

Follow these guidelines when creating git commits to ensure clear, consistent history.

## Guidelines

### 1. Conventional Commits Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

### 2. Commit Types

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting, no code change |
| refactor | Code restructuring |
| perf | Performance improvement |
| test | Adding/updating tests |
| chore | Maintenance tasks |

### 3. Rules

- Keep subject line under 72 characters
- Use imperative mood: "add feature" not "added feature"
- Start with lowercase, no period at end
- Reference issues in footer: `Closes #123`
- Separate subject from body with blank line
- Wrap body at 72 characters

### 4. Examples

```
feat(auth): add OAuth2 login support

Implements OAuth2 authentication flow with Google provider.
Includes token refresh and session management.

Closes #45
```

```
fix(api): handle null response from external service

Returns empty list instead of throwing NullPointerException
when the external API returns null.

Breaks: #67 (but was already broken)
```

### 5. Best Practices

1. Make commits atomic (one logical change per commit)
2. Write meaningful commit messages
3. Commit early, commit often
4. Test before committing
5. Never commit secrets or credentials
