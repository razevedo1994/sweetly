# Sweetly

Internal web app for a small bakery: product catalog + customer orders, Admin and non-Admin Users.
Early scaffold, so there's no runnable app yet. `main.py` is a print stub and no FastAPI app exists.

## Toolchain
- Python 3.12 (`.python-version`), managed with **uv**. Use `uv add` / `uv add --dev`; never pip.
- Lint/format: `uv run ruff check .` and `uv run ruff format .` (default config, no `[tool.ruff]`).
  Run the formatter before committing; formatter-only changes are committed separately as `style: formatter`.
- Tests: `uv run pytest` (no tests exist yet; put them in `tests/`).
- uvicorn is NOT installed. Add it (`uv add uvicorn` or `fastapi[standard]`) before trying to serve the app.

## Design sources (gitignored, so search tools may skip them; read them by path)
- `docs/project_requirements.md`: functional requirements.
- `GLOSSARY.md`: domain vocabulary (User, Admin, Customer, Collected, Archived...). Use these terms in code and docs.
- `docs/SYSTEM_DESIGN.md`: target architecture, routes, the order status lifecycle and env vars.
  Trust the code over this doc when they disagree.
- `texto.md` (untracked): build order: config → models → schemas → auth service →
  `app/dependencies.py` → routers → `main.py` wiring.
- `KNOWN_ISSUES.md`: current bugs in the scaffold. Read it before touching `app/models/`, `app/database.py`,
  `app/config.py`, `app/schemas/` or auth, and remove entries as they get fixed.

## Target architecture (from docs/SYSTEM_DESIGN.md)
- A single FastAPI process renders Jinja2 pages plus HTMX partials. There is no JS build.
  The same endpoint returns a fragment when the request has `HX-Request: true`.
  Partial templates are prefixed with `_` (e.g. `_row.html`).
- Auth is a JWT (PyJWT) in an HttpOnly cookie, enforced by the `get_current_user` and `require_admin` dependencies.
- SQLModel on SQLite. `OrderItems` stores product name/price snapshots so orders survive product edits;
  products are archived (`is_archived`), not deleted.

## Conventions
- Imports are absolute from the `app.` package (`from app.config import settings`). Run commands from the repo root.
- Models reference each other, so use `if TYPE_CHECKING:` imports with string annotations for relationship types
  to avoid circular imports.
- Conventional commits (`feat:`, `style:`, `build:`, `chore:`), small and incremental.
