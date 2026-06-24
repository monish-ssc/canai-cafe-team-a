# Contribution & Branching Guide

Simple flow for a 2-day hackathon — no pull requests, direct merges only.

---

## Branch Structure

```
main
 └── develop
      ├── feat/data-cleaning
      ├── feat/eda-insights
      ├── feat/forecasting-model
      └── feat/powerbi-dashboard
```

| Branch | Purpose |
|--------|---------|
| `main` | Final, presentable state — merge here only at end of Day 2 |
| `develop` | Integration branch — merge your feat branch here when a chunk of work is done |
| `feat/*` | Your personal working branch — one per track |

---

## Day-to-Day Workflow

### 1. Start your feature branch off `develop`
```bash
git checkout develop
git pull origin develop
git checkout -b feat/your-task-description
```

### 2. Commit often as you work
```bash
git add <files>
git commit -m "short description of what you did"
```
Small, frequent commits are better than one giant commit at the end.

### 3. Merge into `develop` when a piece of work is complete
```bash
git checkout develop
git pull origin develop          # grab any changes teammates pushed
git merge feat/your-task-description
git push origin develop
```
Resolve any conflicts locally before pushing.

### 4. Get latest changes from teammates
Do this at the start of each session and after teammates announce they pushed something:
```bash
git checkout develop
git pull origin develop
git checkout feat/your-task-description
git merge develop
```

### 5. Merge `develop` into `main` — end of Day 2 only
Do this once as a team when everything is final:
```bash
git checkout main
git pull origin main
git merge develop
git push origin main
```

---

## Branch Naming

Format: `feat/<short-description>` — lowercase, hyphens, no spaces.

| Track | Example branch name |
|-------|---------------------|
| Data cleaning | `feat/data-cleaning` |
| EDA & insights | `feat/eda-insights` |
| Forecasting model | `feat/forecasting-model` |
| Power BI dashboard | `feat/powerbi-dashboard` |
| Presentation / misc | `feat/presentation` |

---

## Commit Message Format

Keep it short and descriptive:

```
add null handling for transaction_date column
fix duplicate removal logic
add prophet model training script
update regional sales chart in dashboard
```

No need for ticket numbers or fancy prefixes — just say what you did.

---

## Rules

1. **Never commit directly to `main` or `develop`** — always work on a `feat/*` branch.
2. **Pull `develop` before merging into it** — avoid stomping teammates' work.
3. **Do not force push** (`git push --force`) on shared branches (`develop`, `main`).
4. **Announce in the group chat** when you push to `develop` so others can pull.
5. **One person merges to `main`** at the end of Day 2 — agree on who beforehand.

---

## Quick Conflict Resolution

If `git merge` reports conflicts:
```bash
# Open the conflicting file — look for <<<<<<, =======, >>>>>>>
# Edit to keep the correct version
git add <resolved-file>
git commit -m "resolve merge conflict in <file>"
```
When in doubt, call the other person over — don't guess.
