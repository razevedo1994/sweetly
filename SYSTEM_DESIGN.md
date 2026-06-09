# System Design — Sweetly

## 1. Architecture Overview

Sweetly is a single-process web application. FastAPI serves both full-page HTML (via Jinja2 templates) and HTMX partial responses. There is no separate frontend build step or client-side framework.

```
Browser
  └── HTTP/HTTPS
        └── FastAPI (Uvicorn)
              ├── Auth middleware (JWT via HttpOnly cookie)
              ├── Jinja2 templates  ──► full-page HTML
              ├── HTMX partials     ──► HTML fragments (HX-Request)
              └── SQLAlchemy ORM
                    └── SQLite (sweetly.db)
```

All application state is persisted in a single SQLite file. No external services are required.

---

## 2. Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language | Python 3.12+ | Established project language |
| Web framework | FastAPI | Already a dependency; async-capable, good DX |
| Templating | Jinja2 | Ships with FastAPI; sufficient for SSR |
| Dynamic UI | HTMX | Enables SPA-like interactions without a JS build step |
| ORM | SQLAlchemy 2.x | Abstraction over SQLite; enables future DB swap |
| Database | SQLite | Zero-config, file-based; suitable for low volume |
| Auth | JWT (HttpOnly cookie) | Stateless; cookie avoids JS token management |
| Password hashing | bcrypt (passlib) | Industry standard |
| Deployment | Uvicorn (+ optional Docker) | Single command, minimal ops overhead |

---

## 3. Project Structure

```
sweetly/
├── main.py                        # Entry point: creates the FastAPI app
├── pyproject.toml
├── .env                           # Environment variables (not committed)
├── sweetly.db                     # SQLite database file (not committed)
│
├── app/
│   ├── config.py                  # Pydantic Settings — reads from .env
│   ├── database.py                # SQLAlchemy engine, session factory, Base
│   │
│   ├── models/                    # ORM table definitions
│   │   ├── user.py
│   │   ├── category.py
│   │   ├── product.py
│   │   └── order.py               # Order + OrderItem + OrderStatusHistory
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   │
│   ├── routers/                   # FastAPI routers (one per domain)
│   │   ├── auth.py                # /auth/login, /auth/logout
│   │   ├── products.py            # /products, /categories
│   │   └── orders.py              # /orders
│   │
│   ├── services/                  # Business logic (no DB session wiring)
│   │   ├── auth.py                # Token creation/validation, password hashing
│   │   ├── products.py            # Catalog rules (soft-delete, availability)
│   │   └── orders.py              # Order lifecycle, status transitions
│   │
│   ├── dependencies.py            # Shared FastAPI deps: get_db, get_current_user, require_admin
│   │
│   ├── templates/                 # Jinja2 HTML templates
│   │   ├── base.html              # Layout shell (nav, flash messages)
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── products/
│   │   │   ├── list.html
│   │   │   ├── form.html
│   │   │   └── _row.html          # HTMX partial
│   │   └── orders/
│   │       ├── list.html
│   │       ├── detail.html
│   │       ├── form.html
│   │       └── _status_badge.html # HTMX partial
│   │
│   └── static/
│       └── css/
│           └── main.css
│
└── docs/
    ├── project_requirements.md
    └── system_design.md
```

**Naming convention:** HTMX partial templates are prefixed with `_` to distinguish them from full-page templates.

---

## 4. Data Model

### Entity Relationship

```
users ──────────────────┐
  │                     │
  │ created_by          │ changed_by
  ▼                     ▼
orders ◄────── order_status_history
  │
  ▼
order_items
  │
  ▼
products ──► categories
```

### Tables

#### `users`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| username | TEXT UNIQUE NOT NULL | |
| hashed_password | TEXT NOT NULL | bcrypt |
| role | TEXT NOT NULL | `'admin'` or `'staff'` |
| is_active | BOOLEAN NOT NULL | default `true` |
| created_at | DATETIME NOT NULL | default `now()` |

#### `categories`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT UNIQUE NOT NULL | |
| created_at | DATETIME NOT NULL | |

#### `products`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| name | TEXT NOT NULL | |
| description | TEXT | |
| price | DECIMAL NOT NULL | |
| category_id | INTEGER FK → categories | nullable (uncategorized) |
| is_available | BOOLEAN NOT NULL | default `true` |
| is_archived | BOOLEAN NOT NULL | default `false` — soft delete |
| created_at | DATETIME NOT NULL | |
| updated_at | DATETIME NOT NULL | |

#### `orders`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| customer_name | TEXT NOT NULL | |
| status | TEXT NOT NULL | see status lifecycle below |
| total_price | DECIMAL NOT NULL | denormalized for display |
| created_by_id | INTEGER FK → users | |
| created_at | DATETIME NOT NULL | |
| updated_at | DATETIME NOT NULL | |

#### `order_items`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| order_id | INTEGER FK → orders | |
| product_id | INTEGER FK → products | nullable if product archived |
| product_name_snapshot | TEXT NOT NULL | name at time of order |
| unit_price_snapshot | DECIMAL NOT NULL | price at time of order |
| quantity | INTEGER NOT NULL | ≥ 1 |

#### `order_status_history`
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| order_id | INTEGER FK → orders | |
| from_status | TEXT | null for initial creation |
| to_status | TEXT NOT NULL | |
| changed_by_id | INTEGER FK → users | |
| changed_at | DATETIME NOT NULL | |

### Order Status Lifecycle

```
                 ┌─────────────┐
                 │   PENDING   │◄─── creation
                 └──────┬──────┘
                        │ (any user)
                        ▼
               ┌────────────────┐
               │ IN_PREPARATION │
               └───────┬────────┘
                        │ (any user)
                        ▼
                 ┌─────────────┐
                 │    READY    │
                 └──────┬──────┘
                        │ (any user)
                        ▼
               ┌────────────────┐
               │   DELIVERED    │
               └────────────────┘

  CANCELLED ◄── any status (admin only)
```

---

## 5. API & Route Design

HTMX requests are identified by the `HX-Request: true` header. Endpoints return HTML fragments for HTMX requests and full pages otherwise. The same router handles both.

### Auth — `/auth`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/auth/login` | Public | Login page |
| POST | `/auth/login` | Public | Validate credentials, set JWT cookie |
| POST | `/auth/logout` | Any | Clear JWT cookie |

### Products — `/products`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/products` | Any | List products (filter by category, availability) |
| GET | `/products/new` | Admin | New product form |
| POST | `/products` | Admin | Create product |
| GET | `/products/{id}/edit` | Admin | Edit form |
| PUT | `/products/{id}` | Admin | Update product |
| DELETE | `/products/{id}` | Admin | Soft-archive product |
| PATCH | `/products/{id}/availability` | Admin | Toggle availability |

### Categories — `/categories`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/categories` | Any | List categories |
| POST | `/categories` | Admin | Create category |
| PUT | `/categories/{id}` | Admin | Rename category |
| DELETE | `/categories/{id}` | Admin | Delete (only if no active products) |

### Orders — `/orders`
| Method | Path | Role | Description |
|--------|------|------|-------------|
| GET | `/orders` | Any | List orders (filter by status, date range) |
| GET | `/orders/new` | Any | New order form |
| POST | `/orders` | Any | Create order |
| GET | `/orders/{id}` | Any | Order detail + status history |
| PUT | `/orders/{id}` | Any | Edit order (only while `PENDING`) |
| PATCH | `/orders/{id}/status` | See lifecycle | Advance status |
| DELETE | `/orders/{id}` | Admin | Cancel order |

---

## 6. Authentication Flow

```
1. User submits POST /auth/login
2. Service verifies username + bcrypt hash
3. FastAPI generates JWT with payload: { sub: user_id, role: "admin"|"staff", exp: now + SESSION_TTL }
4. JWT is set as HttpOnly, Secure, SameSite=Lax cookie
5. Browser sends the cookie automatically on every subsequent request
6. `get_current_user` dependency decodes and validates the JWT on each request
7. `require_admin` dependency raises HTTP 403 if role != "admin"
8. POST /auth/logout clears the cookie (client-side expiry)
```

JWT secret and TTL are read from environment variables (`JWT_SECRET`, `SESSION_TTL_MINUTES`).

---

## 7. Configuration & Environment Variables

Managed via a `.env` file read by `pydantic-settings` in `app/config.py`.

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./sweetly.db` |
| `JWT_SECRET` | Signing secret for JWTs | random 32-byte hex string |
| `SESSION_TTL_MINUTES` | JWT lifetime in minutes | `480` (8 hours) |
| `DEBUG` | Enable FastAPI debug mode | `false` |

---

## 8. Deployment

### Without Docker (development)

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### With Docker Compose (production)

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./sweetly.db:/app/sweetly.db
    restart: unless-stopped
```

```bash
docker compose up -d
```

The SQLite file is bind-mounted so data survives container restarts and can be backed up by copying the file.
