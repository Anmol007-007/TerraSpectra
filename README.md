# TerraSpectra — IDE Project Pack

Hyperspectral Crop Disease Forecasting (3D-CNN + ViT, FastAPI, React + Deck.gl).
This pack tells your IDE/AI assistant everything needed to build the project in **20 days × 52 commits**.

## Setup (2 minutes)
```bash
mkdir terraspectra && cd terraspectra && git init -b main
# copy EVERYTHING from this pack into the repo root (including dotfiles: .cursorrules, .github/)
git add -A && git commit -m "docs: add IDE project pack"
```
Your IDE auto-reads: `AGENTS.md` (Codex/Claude Code/generic), `CLAUDE.md`, `.cursorrules` (Cursor), `.github/copilot-instructions.md` (Copilot).

## Contents
| Path | What it is |
|---|---|
| `AGENTS.md` (+ copies) | Master rules, protocol, coding standards, domain facts |
| `docs/01–10` | Spec, architecture, repo tree, stack, data, ML, API, frontend, git protocol, QA |
| `plan/DAY_01..20.md` | 52 numbered checklist commits per day, with exact commit messages (1,040 total) |
| `plan/README.md` | Day index |
| `scripts/check_commits.sh` | Verifies >= 52 commits today |

## Prompts to paste into your IDE
**Start of each day:**
> Read AGENTS.md and the docs it references. Today is Day N. Open plan/DAY_NN.md and execute the 52 steps in order. After each step, run lint + relevant tests and make exactly one commit with the given message. Stop after step 52 and run scripts/check_commits.sh.

**If you fall behind:** "Continue plan/DAY_NN.md from the first unchecked step."

**Mid-day resume:** "Run `git log --oneline -n 60` to see which steps are done, then continue."

## Note on commit counts
Steps are real, small, atomic changes (a function, a test, a config) so 52/day is natural. Don't add empty or whitespace commits to hit the number — if short, split a step into a smaller meaningful one (e.g., separate test from implementation).
