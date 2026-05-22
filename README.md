# Ad Campaign Management — Backend

A production-ready REST API and real-time notification system for managing advertising campaigns, built with FastAPI and PostgreSQL.

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Auth:** JWT (access + refresh tokens) via HTTP-only cookies
- **Real-Time:** WebSockets (native FastAPI)
- **Validation:** Pydantic v2
- **Rate Limiting:** SlowAPI
- **Password Hashing:** Bcrypt

---

## Project Structure

```
app/
├── config/
│   ├── database_config.py       # SQLAlchemy engine + session + init_db
│   └── settings.py              # Environment variables via pydantic-settings
├── core/
│   ├── alert_engine.py          # Evaluates campaign metrics against alert rules
│   ├── exceptions.py            # Custom exception classes
│   ├── limiter.py               # SlowAPI rate limiter instance
│   ├── security.py              # JWTBearer dependency, token helpers
│   └── websocket_manager.py     # WebSocket connection manager
├── helpers/
│   ├── messages.py              # Reusable response message strings
│   └── transformers.py          # SQLAlchemy model → dict transformers
├── models/
│   ├── campaign_model.py        # Campaign SQLAlchemy model
│   ├── notification_models.py   # Notification + AlertRule models
│   └── user_model.py            # User SQLAlchemy model
├── repository/
│   ├── base_repository.py       # Generic CRUD base class
│   ├── alert_rule_repository.py # AlertRule DB operations
│   ├── campaigns_repository.py  # Campaign DB operations
│   ├── notification_repository.py # Notification DB operations
│   └── user_repository.py      # User DB operations
├── routers/
│   ├── routes.py                # V1 + V2 route registration
│   ├── responses.py             # Standardized response helpers
│   ├── campaign_routes.py       # Campaign CRUD endpoints
│   ├── notification_routes.py   # Notification + alert rule endpoints
│   └── user_authentication.py  # Auth endpoints
├── schemas/
│   ├── campaign_schema.py       # Campaign Pydantic schemas
│   ├── notification_schema.py   # Notification + AlertRule schemas
│   └── user_auth_schema.py      # User auth schemas
└── services/
    ├── base_service.py          # Base service class
    ├── campaign_service.py      # Campaign business logic
    ├── notification_service.py  # Notification + alert logic
    └── user_service.py          # User business logic
main.py                          # FastAPI app entry point
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
PROJECT_NAME=AdNexus
PROJECT_VERSION=1.0.0

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/adnexus

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173"]

# API prefixes
API_V1_STR=/api/v1
API_V2_STR=/api/v2
```

### Run the Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8090
```

API docs available at: `http://127.0.0.1:8090/docs`

---

## API Reference

### Auth — `/api/v1/auth`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/signup` | Register new user | No |
| POST | `/login` | Login + set refresh cookie | No |
| POST | `/logout` | Logout + clear cookie | No |
| POST | `/refresh` | Refresh access token | No |
| GET | `/` | Get user profile | Yes |
| PATCH | `/` | Update user profile | Yes |
| POST | `/` | Change password | Yes |
| DELETE | `/` | Delete account | Yes |

### Campaigns — `/api/v2/campaign`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List campaigns (paginated, filterable) | Yes |
| POST | `/` | Create campaign | Yes |
| GET | `/{id}` | Get single campaign | Yes |
| PATCH | `/` | Update campaign | Yes |
| DELETE | `/` | Delete campaign | Yes |

**Query params for GET `/`:** `page`, `limit`, `client`

### Notifications — `/api/v1/notifications`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| WS | `/ws/{user_id}` | WebSocket connection | No |
| GET | `/` | Get notifications | Yes |
| GET | `/unread-count` | Get unread count | Yes |
| PATCH | `/read` | Mark all as read | Yes |
| PATCH | `/{id}/read` | Mark one as read | Yes |
| POST | `/rules` | Create alert rule | Yes |
| GET | `/rules` | Get user's rules | Yes |
| DELETE | `/rules/{id}` | Delete rule | Yes |
| PATCH | `/rules/{id}/toggle` | Toggle rule on/off | Yes |

---

## Alert Rule Engine

When a campaign is updated, the engine evaluates all active rules for that campaign and fires a WebSocket notification for any breached thresholds.

Supported alert types:

| Type | Trigger |
|------|---------|
| `ctr_low` | CTR drops below threshold % |
| `spend_high` | Spend exceeds threshold % of budget |
| `roas_low` | ROAS drops below threshold × |
| `budget_exceeded` | Spend exceeds budget |
| `conversions_low` | Conversions drop below threshold |

Default rules are auto-created when a campaign is created.

---

## Architecture

```
Route → Service → Repository → Database
         ↓
    NotificationService
         ↓
    AlertEngine → WebSocketManager → Browser
```

- **Routes** handle HTTP/WS, call services via FastAPI `Depends()`
- **Services** contain business logic, call repositories
- **Repositories** extend `BaseRepository`, handle all DB operations
- No `db` session ever appears in routes or services

---

## Rate Limiting

Global default: `100 requests/minute` per IP.
Login endpoint: `5 requests/minute`.

Behind a proxy, real client IP is read from the `X-Forwarded-For` header.
