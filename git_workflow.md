# Git Workflow & Version Control Guidelines

This document serves as the authoritative guide for all version control actions within this project. It is strictly enforced to maintain an auditable, intentional, and clean Git history.

## 1. Initial Repository Setup & Publishing

To initialize a new repository and push it to a remote, follow these exact steps:

```bash
# 1. Initialize local repository
git init

# 2. Add all tracked files
git add .

# 3. Create initial commit
git commit -m "Initial commit"

# 4. Set the main branch
git branch -M main

# 5. Add remote (temporary token use if necessary)
git remote add origin https://<TOKEN>@github.com/<USER>/<REPO>.git

# 6. Push to remote
git push -u origin main

# 7. Security Cleanup (crucial if a token was used)
git remote remove origin
git remote add origin https://github.com/<USER>/<REPO>.git
```

## 2. Common Workflows

### Branching
Always create a feature branch before beginning new work:
```bash
git checkout -b feature/name-of-feature
```

### Committing
Commits must be atomic and well-documented.
```bash
git add <specific_files>
git commit -m "Brief summary of changes"
```

### Pulling and Fetching
Always pull changes using `--rebase` to avoid messy merge commits.
```bash
git fetch origin
git pull --rebase origin main
```

### Merging
When a feature is complete, merge it into `main`:
```bash
git checkout main
git merge --no-ff feature/name-of-feature
git push origin main
```

## 3. Recovery and Dangerous Commands

> [!WARNING]
> Do NOT run these commands without explicit justification and permission.

- **Resetting History**: `git reset --hard HEAD~1` (Destroys the most recent commit and working directory changes).
- **Force Pushing**: `git push --force` or `git push --force-with-lease` (Overwrites remote history. Only allowed on private feature branches, NEVER on `main`).
- **Cleaning History**: `git rebase -i` (Used to squash commits or remove accidental sensitive data. Must be documented).

## 4. Automation & History Scrubbing
If sensitive data (like API keys) accidentally leaks into the commit history, consult the `git_history_sanitization` knowledge base procedures for utilizing `git-filter-repo` or interactive rebasing to permanently purge the data before force-pushing.
