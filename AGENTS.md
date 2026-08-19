# AGENTS.md

Instructions for AI coding agents (Claude Code, Codex, Cursor, Copilot agents, …)
working on **ScrapeGraphAI**. Human contributors should read
[CONTRIBUTING.md](CONTRIBUTING.md); everything here is in addition to it.

---

## 1. Golden rule: everything goes to `pre/beta`

**`main` is never written to directly. All work is based on and merged into `pre/beta`.**

`pre/beta` is the prerelease branch: pushes to it publish a `beta` prerelease via
semantic-release (see `.releaserc.yml`). `main` only receives releases when a
maintainer promotes `pre/beta`.

```bash
# 1. always start from an up-to-date pre/beta
git fetch origin
git checkout -b feat/my-change origin/pre/beta

# 2. commit your work
git add <only the files you touched>
git commit -m "feat(nodes): add X"

# 3. push and open the PR against pre/beta
git push -u origin feat/my-change
gh pr create --base pre/beta --title "feat(nodes): add X" --body "..."
```

Checklist before you commit:

- [ ] The branch is based on `origin/pre/beta` (`git merge-base --is-ancestor origin/pre/beta HEAD`).
- [ ] The PR base is `pre/beta`, **not** `main`.
- [ ] No commits directly on `main` or `pre/beta`, no force-push to either.
- [ ] One logical change per branch/PR.

If a task genuinely requires targeting `main` (e.g. a hotfix on a released
version), stop and ask a maintainer first.

## 2. Environment setup

Python `>=3.12`, dependencies managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync                     # create the venv and install deps
uv run pre-commit install   # install the git hooks
```

Never hand-edit `uv.lock`; regenerate it with `uv lock` / `uv sync` and commit
the result only when you actually changed dependencies in `pyproject.toml`.

## 3. Checks to run before pushing

```bash
make lint         # ruff + black --check + isort --check-only
make type-check   # mypy (strict)
make test         # pytest with coverage
make pre-commit   # run all hooks on all files
```

Run at least `make lint` and the tests covering what you touched. Report the
real result: if something fails or you skipped a step, say so in the PR
description instead of implying a clean run.

Style: PEP 8 + Google Python docstrings, `black` formatting, line length 88.
Match the conventions of the surrounding file rather than introducing new ones.

## 4. Commit messages

Commits are parsed by semantic-release (Conventional Commits, `conventionalcommits`
preset), so the message decides the next version number. Use:

```
feat:     ✨ new feature          -> minor bump
fix:      🐛 bug fix              -> patch bump
docs:     📚 documentation
style:    💅 formatting only
refactor: ♻️  no behaviour change
perf:     ⚡ performance
test:     🧪 tests
build:    📦 build system / deps
ci:       🤖 CI configuration
chore:    🧹 everything else
```

Format: `type(optional-scope): imperative summary`, optional body, and
`BREAKING CHANGE:` in the footer for incompatible changes. Reference issues with
`Fixes #123`.

## 5. Files agents must not touch

- `CHANGELOG.md` and the `version` field in `pyproject.toml` — owned by
  semantic-release; editing them by hand breaks releases.
- Git tags and release notes on GitHub.
- `.github/workflows/*` — only when the task is explicitly about CI.
- Anything under `htmlcov/`, `coverage.xml`, `.pytest_cache/`, `__pycache__/`:
  build artifacts, never commit them.

Also: never commit secrets. API keys go in a local `.env` (git-ignored) and are
read via `os.getenv`; examples and tests must use placeholders such as
`OPENAI_APIKEY` from the environment.

## 6. Repository layout

```
scrapegraphai/
├── graphs/        # pipelines (SmartScraperGraph, SearchGraph, …)
├── nodes/         # single graph steps (FetchNode, ParseNode, GenerateAnswerNode, …)
├── models/        # LLM wrappers and token/model metadata
├── docloaders/    # loaders (ChromiumLoader, …)
├── prompts/       # prompt templates
├── helpers/       # shared constants and schemas
├── integrations/  # third-party / managed-API integrations
└── utils/         # utilities (html cleanup, tokenization, …)
examples/          # runnable usage examples, one folder per graph
tests/             # pytest suite, mirrors the package layout
docs/              # documentation sources
```

When adding a node or graph, register it in the corresponding `__init__.py` and
add a test under `tests/` next to the existing ones for that layer. New
user-facing features need an entry in `examples/` and, when they change public
behaviour, a docs update.

## 7. Working style expected from agents

- Prefer small, reviewable diffs; do not reformat or "clean up" untouched files.
- Do not add dependencies unless the task requires it — say why in the PR.
- Write all commits, PR titles/bodies, issue comments, code comments and
  docstrings **in English**.
- Do not delete or rewrite existing tests to make a change pass.
- If a test is already failing on `pre/beta`, mention it rather than silently
  fixing unrelated things in the same PR.
- Never commit other people's in-progress work: check `git status` and stage
  only the files belonging to your change.
