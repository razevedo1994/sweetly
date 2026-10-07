# Sweetly

Internal web app for a small bakery to manage its product catalog and customer orders. It has Admin and non-Admin Users and is not customer-facing.

> **Status:** early scaffold. There is no runnable app yet: `main.py` is a print stub and no FastAPI app exists.

## Planned features

- **Authentication:** username/password login, with a JWT in an HttpOnly cookie and a configurable session timeout.
- **Product catalog:** products with categories and an available/unavailable flag. Admins create, edit, archive and restore products; archived products are never deleted.
- **Orders:** any User creates an order for a Customer (name + phone). Orders move forward through **Pending → In Preparation → Ready → Collected**. Only an Admin can cancel, and only while the order is Pending.
- **Order list and history:** filter orders by status and date range, see an order's status history, and view all orders of a Customer.

## Tech stack

- Python 3.12, managed with [uv](https://docs.astral.sh/uv/)
- FastAPI, with Jinja2 pages and HTMX partials (no JS build)
- SQLModel on SQLite
- pydantic-settings for config, PyJWT for auth, passlib/bcrypt for password hashing
- pytest and ruff

## Getting started

```bash
uv sync                    # install dependencies
uv run ruff check .        # lint
uv run ruff format .       # format
uv run pytest              # tests (none yet; put them in tests/)
```

Serving the app isn't possible yet. Once it exists, add uvicorn first (`uv add uvicorn`).

Configuration is planned to come from a `.env` file:

| Variable              | Description                                   |
| --------------------- | --------------------------------------------- |
| `DATABASE_URL`        | SQLAlchemy URL, e.g. `sqlite:///./sweetly.db` |
| `JWT_SECRET`          | Signing secret for JWTs                       |
| `SESSION_TTL_MINUTES` | Session lifetime in minutes                   |
| `DEBUG`               | Enable FastAPI debug mode                     |

## Project structure

```
main.py             # entry point (stub)
app/
├── config.py       # settings
├── database.py     # engine and session
├── models/         # SQLModel tables: user, category, product, order
├── schemas/        # request/response schemas
├── routers/        # FastAPI routers (empty)
└── services/       # business logic (auth)
```

Still to come: `app/dependencies.py` (`get_current_user`, `require_admin`), `app/templates/` and `app/static/`.
