# 09 — Git Commit Protocol
- Conventional Commits: `type(scope): imperative summary` — types: feat fix docs test refactor perf build ci chore style.
- Daily commit workflow: Complete all tasks and checklist items for that day, verify linting and tests, clean up temporary files, and commit everything at the end of the day all at once before pushing to `main`.
- Never `--allow-empty`, never whitespace padding.
- Branching: `main` (protected, always green) · optional `day/XX-short-name` per day, merged or pushed into `main` at day end.
- Tags: `v0.1.0` (Day 10 mid review), `v0.2.0` (Day 15), `v0.3.0` (Day 19), `v1.0.0` (Day 20).
- Large files: Git LFS for `*.tif *.h5 *.pt *.onnx` if you must commit samples (keep < 5 MB samples under `tests/fixtures`).
- Daily ritual: Work daily plan tasks → run lint & tests → clean temporary files → commit day's work → push to main.
