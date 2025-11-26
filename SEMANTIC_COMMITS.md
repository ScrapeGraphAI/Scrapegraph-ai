# Semantic Commit Format for This PR

## Current Situation

This PR contains commits that need to be rewritten to follow Conventional Commits format for semantic-release compatibility.

## Commits to Rewrite

### Commit 1: 9439fe5
**Current:** `Fix langchain import issues blocking tests`

**Should be:**
```
fix(imports): update deprecated langchain imports to langchain_core

Update imports from deprecated langchain.prompts to langchain_core.prompts
across 20 files to fix test suite import errors. These changes address
breaking API changes in newer langchain versions.

Fixes #1015
```

**Type:** `fix` - Bug fix for test import errors
**Scope:** `imports` - Changes affect import statements

---

### Commit 2: 323f26a  
**Current:** `Add comprehensive timeout feature documentation`

**Should be:**
```
docs(timeout): add comprehensive timeout configuration guide

Add detailed documentation for FetchNode timeout feature including:
- Configuration examples with different timeout values
- Use cases for HTTP requests, PDF parsing, and ChromiumLoader
- Graph integration examples
- Best practices and troubleshooting guide

The timeout feature was already implemented in the base code and this
documentation helps users configure and use it effectively.

Fixes #1015
```

**Type:** `docs` - Documentation changes only
**Scope:** `timeout` - Related to timeout feature documentation

---

## How to Apply (For Maintainer)

Since automated tools can't force-push to rewrite history, the maintainer needs to manually rewrite these commits:

### Option 1: Interactive Rebase
```bash
git rebase -i 6d13212
# Mark commits 9439fe5 and 323f26a as 'reword'
# Update commit messages with semantic format above
# Force push: git push --force-with-lease
```

### Option 2: Squash and Rewrite
```bash
# Reset to initial commit
git reset --soft 6d13212

# Stage import fixes
git add scrapegraphai/

# Commit with semantic message
git commit -m "fix(imports): update deprecated langchain imports to langchain_core

Update imports from deprecated langchain.prompts to langchain_core.prompts
across 20 files to fix test suite import errors. These changes address
breaking API changes in newer langchain versions.

Fixes #1015"

# Stage documentation
git add docs/

# Commit with semantic message
git commit -m "docs(timeout): add comprehensive timeout configuration guide

Add detailed documentation for FetchNode timeout feature including:
- Configuration examples with different timeout values
- Use cases for HTTP requests, PDF parsing, and ChromiumLoader
- Graph integration examples
- Best practices and troubleshooting guide

The timeout feature was already implemented in the base code and this
documentation helps users configure and use it effectively.

Fixes #1015"

# Force push
git push --force-with-lease origin copilot/add-timeout-to-fetch-node
```

## Semantic Release Configuration

This repository uses `@semantic-release/commit-analyzer` with `conventionalcommits` preset (see `.releaserc.yml`).

Valid types for this repo:
- `feat`: New features → Minor version bump
- `fix`: Bug fixes → Patch version bump
- `docs`: Documentation changes → No version bump (shown in changelog)
- `chore`: Maintenance tasks
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test changes

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Release](https://semantic-release.gitbook.io/)
- Repository config: `.releaserc.yml`
