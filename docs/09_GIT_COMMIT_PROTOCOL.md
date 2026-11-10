# 09 — Git Commit Protocol (>= 52 commits/day)
- Conventional Commits: `type(scope): imperative summary` — types: feat fix docs test refactor perf build ci chore style.
- 1 plan step = 1 commit. Commit immediately after the step passes lint/tests. Keep each diff small but real.
- Never `--allow-empty`, never whitespace padding, never mass-rewrite to inflate counts.
- Branching: `main` (protected, always green) · `day/XX-short-name` per day, merged with `--no-ff` at day end (merge commit not counted in the 52).
- Tags: `v0.1.0` (Day 10 mid review), `v0.2.0` (Day 15), `v0.3.0` (Day 19), `v1.0.0` (Day 20).
- Daily check: `scripts/check_commits.sh` (counts commits authored today on current branch vs main base).
- Large files: Git LFS for `*.tif *.h5 *.pt *.onnx` if you must commit samples (keep < 5 MB samples under `tests/fixtures`).
- Daily ritual: `git checkout -b day/XX-name` → work steps → `scripts/check_commits.sh` → push → PR/merge.
