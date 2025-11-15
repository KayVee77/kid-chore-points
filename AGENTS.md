# AGENTS.md — ChorePoints (Taškų Nuotykis)

This file is an agent-focused guide for coding agents (OpenAI Codex, GitHub Copilot, VS Code agents, etc.).
It holds the key commands, policies, and conventions agents must follow when working on this repository.

## Project Overview (for agents)
- Repo: kid-chore-points — Django 5 app for kid chores with point tracking and parent approval workflow.
- Language: Python 3.11
- Single app: `core/` contains models, views, admin, management commands, template and static assets.
- Production: Azure App Service (app: `elija-agota`), Postgres Flexible Server (`chorepoints-db`), Azure Blob Storage (`chorepointsstorage`).
- CI/CD: GitHub Actions triggers on `main` and special PR jobs (see `.github/workflows/deploy.yml`).

> Agents: prefer using the nearest `AGENTS.md` for any subfolder. This file is the global default.

## Quick Setup commands (local dev; PowerShell on Windows)
- Install dependencies, create virtual env, apply migrations and start dev server:
```powershell
cd chorepoints
./dev.ps1
```
- Fast start (activate venv + start server if already created):
```powershell
cd chorepoints
./run.ps1
```
- Seed local demo (seed_demo_lt loads a small set of data for testing):
```powershell
python manage.py seed_demo_lt --username <parent_username>
# Or load from CSV for production-like data
python manage.py load_initial_data
```

## Build / Docker
- Dockerfile exists at `chorepoints/Dockerfile` — use for containerizing app.
- Build and run locally using docker-compose declared in `docker-compose.yml` (top-level); if not, build image manually:
```bash
cd chorepoints
docker build -t kid-chore:local .
# Run the container (expose port 8000) and postgres
docker-compose up -d
```

## Tests & Playwright E2E
- Unit tests live under `core/tests/` — run with pytest (placeholder)
```bash
# (Optional) install pytest
pip install pytest pytest-django
pytest core/tests
```
- End-to-end tests (Playwright) are recommended to cover: kid login, chore submission, parent approval, confetti trigger.
  - Tests should be in `e2e/tests/` and follow UID/data-test attributes where possible.
  - To run local, start app then run the Playwright environment:
```bash
# Install node & playwright
cd e2e
npm install
npx playwright install --with-deps
npx playwright test
```
- In CI: run Playwright tests against staging App Service or a container running the `chorepoints` image.

## Code style & linting
- Python: follow PEP8. Use `black` and `flake8` if present.
- Keep template strings localized to Lithuanian for kid-facing UI. Admin text can be English.
- Use atomic DB transactions for any balance/money-like updates — see `models.py` (`transaction.atomic()` pattern used for approve()/reject() methods).

## PR instructions (agent-friendly)
- Always branch from `main`: `git checkout -b feature/<short-descr>`
- Run `./dev.ps1` locally and verify the following:
  - migrations applied
  - local HTTP routes operate: `/`, `/admin/`, `/kid/login/`
  - seed data present (run `seed_demo_lt` or `load_initial_data`)
- Commit descriptive messages with the format: `[<scope>] <short change> — <why>`
- Create PR, set reviewers, and include: 'What I changed' + 'Testing steps' + 'Any migration steps'
- DO NOT merge to `main` - user or maintainer will merge for production. Agents must stop at creating a PR.

## Environments & secrets
- Do not store secrets in the repo. Use Azure App Service settings for production secrets.
- Production required envs: `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY`.
- For local dev, `dev.ps1` handles a local SQLite DB. Add `.env` values or use `./dev.ps1` default.

## Deployment steps (for agents to prepare PRs)
- CI will auto-build and deploy `main` to Azure App Service. Agents should:
  1. Create a feature branch.
  2. Make changes locally and add tests.
  3. Create PR and let user/maintainer review & merge.
  4. After merge, deployment happens automatically. The human should ssh and run `python manage.py load_initial_data` if CSV changed.
- For containerization, we use `Dockerfile` + `docker-compose.yml` for local testing and GitHub Actions to push images to ACR then App Service.

## Data & migrations
- CSV data in `chorepoints/initial_data/` — `load_initial_data` loads them; `seed_demo_lt` seeds demonstration data.
- Avoid changing CSV format unless you update `load_initial_data` accordingly.
- When adding new model fields, add migrations: `python manage.py makemigrations core` → `python manage.py migrate`.

## Security & Best Practices
- PINs are plaintext for MVP and documented as such — don't change this without a migration plan.
- Always use `transaction.atomic()` when altering `Kid.points_balance` or `Kid.map_position`.
- Admin actions should require a review step before mass `approve()` operations.

## What agents must not do (policy)
- Never push directly to `main`. Always open a PR.
- Do not change production secrets or Azure config without explicit human approval.
- Do not run `az webapp ssh` or remote commands yourself — instead, include instructions and ask the human to run them (Copilot-instructions: rules around SSH are in `.github/copilot-instructions.md`).

## Agent-specific tips
- Use short, actionable commits and split changes into minimal PRs.
- Add or update tests whenever you modify behaviour (models, views, approval flow).
- For UI changes, add snapshot or functional tests in Playwright or update templates accordingly.
- When writing migration changes, include a reversible migration if possible.
- Keep changes to production configuration minimal and clearly documented in PR description.

## Extra: how to run a smoke test locally
1. Start server: `./dev.ps1` (Windows) or `python manage.py runserver` (Unix)
2. Seed demo data: `python manage.py seed_demo_lt --username <admin>`
3. Create a PENDING chore as a kid, approve it in admin, verify points updated and confetti flag in session.

## Conflict resolution (agents)
If tests fail on CI or merge conflict occurs, agents should:
1. Pull `main` and rebase your feature branch.
2. Run tests locally to reproduce failures.
3. If failure is intermittent/flaky, add retries to Playwright tests or debug & fix.

## References
- `.github/copilot-instructions.md` — Agent-specific rules for AI agents (priority rules, never push `main`, admin approval rules)
- `chorepoints/initial_data/` — CSV definition for chores and rewards
- `chorepoints/core/models.py` — Where approval logic and `approval()` methods are implemented

---

If you want me to add a smaller `AGENTS.md` for the `core/` subfolder specifically (scoped guidance for model and views tasks), I can add `core/AGENTS.md` with local steps (e.g., run `python manage.py test core`).

