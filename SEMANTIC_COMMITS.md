# Semantic Commit Format for This PR

## Current Situation

This PR contains commits that need to be rewritten to follow Conventional Commits format for semantic-release compatibility.

**Note:** The timeout documentation is marked as `feat(timeout)` (not `docs`) because it exposes a user-facing feature. Even though the implementation existed, this PR makes the feature discoverable and usable by users through documentation, which warrants a feature-level semantic version bump.

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
feat(timeout): add configurable timeout support for FetchNode

Add comprehensive documentation for the timeout configuration feature:
- Configuration examples with different timeout values
- Use cases for HTTP requests, PDF parsing, and ChromiumLoader
- Graph integration examples
- Best practices and troubleshooting guide

The timeout feature enables users to control execution time for blocking
operations (HTTP requests, PDF parsing, ChromiumLoader) to prevent
indefinite hangs. Configurable via node_config with 30s default.

Fixes #1015
```

**Type:** `feat` - New feature documentation/exposure to users
**Scope:** `timeout` - Timeout configuration feature

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
git commit -m "feat(timeout): add configurable timeout support for FetchNode

Add comprehensive documentation for the timeout configuration feature:
- Configuration examples with different timeout values
- Use cases for HTTP requests, PDF parsing, and ChromiumLoader
- Graph integration examples
- Best practices and troubleshooting guide

The timeout feature enables users to control execution time for blocking
operations (HTTP requests, PDF parsing, ChromiumLoader) to prevent
indefinite hangs. Configurable via node_config with 30s default.

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
