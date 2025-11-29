# RPG Consent Finder

RPG Consent Finder helps tabletop groups capture and share their consent and play-style preferences. The application delivers a NiceGUI front end backed by SQLModel for persistence and a lightweight service layer that keeps UI code declarative and testable.

---

## Architecture Overview

- **Presentation**: NiceGUI `pages/*.py` build the interactive UI. Long handlers are decomposed into helper functions and reusable components under `src/components`. Guided tours walk new players through key flows.
- **Controllers**: `src/controller/*` expose thin adapters that maintain backward compatibility with existing imports while delegating to services.
- **Service Layer**: `src/services/*.py` owns business rules such as group lifecycle (`group_service`) and consent sheet creation (`sheet_service`). Functions accept optional SQLModel sessions so they can participate in larger transactions or be isolated in tests.
- **Persistence**: SQLModel models in `src/models/db_models.py` define users, groups, sheets, and linking tables. `models.model_utils.session_scope` standardises session lifecycle management.
- **Settings & Logging**: `src/settings.py` supplies a cached `Settings` dataclass. Logging is configured via `src/a_logger_setup.py` to avoid side effects at import time.

---

## Data Model Cheatsheet

- `User`: authentication identity containing NiceGUI storage ids, nickname, and consent sheets.
- `ConsentSheet`: per-user sheet composed of multiple `ConsentEntry` records populated from `ConsentTemplate` definitions.
- `RPGGroup`: campaign grouping with GM ownership, unique invite code, and many-to-many links to consent sheets (`GroupConsentSheetLink`) and members (`UserGroupLink`).
- `ConsentStatus`: enum backing the traffic-light style consent options shown in the UI.

The service layer hides the join-table manipulation so most call sites work with `User`, `ConsentSheet`, and `RPGGroup` instances directly.

---

## Development Workflow

1. **Install dependencies**
   ```ps1
   poetry install
   ```
2. **Run the development server**
   ```ps1
   poetry run python .\src\main.py --reload
   ```
3. **Execute tests with coverage guard**
   ```ps1
   poetry run pytest
   ```
   The suite must meet the configured `fail-under=70` coverage threshold. Targeted test runs (for example `pytest tests/test_group.py`) are useful during refactors but still enforce the global gate.
4. **Format and lint**
   - The project currently relies on editor/CI tooling for formatting. Keep functions small, prefer service helpers for business logic, and add concise comments only when intent is non-obvious.

---

## Environment Configuration

- `DB_CONNECTION_STRING`: database connection URL (default `sqlite:///db/database.sqlite`).
- `LOGLEVEL`: python logging level (default `INFO`).
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: OAuth values for Google login.
- `DISCORD_CLIENT_ID` / `DISCORD_CLIENT_SECRET`: OAuth values for Discord login.
- `BASE_URL`: external URL for callback construction, default `http://localhost:8080`.
- `ADMINS`: comma separated list of `User.id_name` values that receive admin rights.
- `SEED_ON_STARTUP`: bootstrap the database with sample data (`False` by default).
- `RELOAD`: toggles auto-reload during development (default `False`).
- `STORAGE_SECRET`: secret used by NiceGUI to encrypt session storage (random per start when omitted).

**Quick start snippet (PowerShell):**
```ps1
$env:DB_CONNECTION_STRING = "sqlite:///db/database.sqlite"
$env:LOGLEVEL = "INFO"
$env:SEED_ON_STARTUP = "true"
$env:RELOAD = "true"
```

---

## Database Migrations (Alembic)

Alembic is already configured via `alembic.ini` and the scripts under `migrations/`. Use it to keep the SQLite (or Postgres) schema in sync with the SQLModel definitions.

1. **Make your model changes** in `src/models/db_models.py` (or related files) and ensure they import cleanly.
2. **Autogenerate a revision** with Poetry's environment:
   ```ps1
   poetry run alembic revision --autogenerate -m "describe_change"
   ```
   Alembic reads the `DB_CONNECTION_STRING` env var, so point it at the database you want to diff before running the command.
3. **Review the generated file** under `migrations/versions/` to verify the `upgrade()`/`downgrade()` logic looks correct; edit as needed for custom data moves.
4. **Apply the migration** locally with:
   ```ps1
   poetry run alembic upgrade head
   ```
   Run the same command in staging/production (with the appropriate connection string) when deploying.

Helpful extras:
- `poetry run alembic history` shows the revision graph.
- `poetry run alembic downgrade -1` rolls back the last migration if you need to redo it during development.

---

## Roadmap Snapshot

Tracked tasks that still need attention:

- Guided tour coverage for import/export flows.
- Additional automated tests (playstyle scoring, feedback loop, import/export edge cases, localisation fallbacks).
- Integrate radar plot summaries into group views and provide campaign-level summaries.
- Anonymous public sheets with passcode protection and printable/PDF exports.
- Performance work: caching hot localisation lookups and reducing N+1 queries.
- Prompt users to rename generated sheet and group titles.
- Investigate migration path from SQLite to PostgreSQL for production deployments.
