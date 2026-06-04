# API Service — Remaining Agent Tasks

## What is already built (do not rebuild)
- `main.py` — FastAPI app, `/analyze` + `/report/{id}` routes fully working with in-memory store
- `schemas.py` — Pydantic request/response models with validation
- `store.py` — In-memory ReportRecord store (MVP, replace with DB)
- `tests/test_api.py` — Gate tests for analyze + report flow
- All auth routes return HTTP 501 with a clear message

## What you need to build

---

### Task A: Database (replaces in-memory store)

**Complexity: Medium. Requires: DATABASE_URL (Neon or Supabase free tier)**

1. Create `database.py`:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(os.getenv("DATABASE_URL"), echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass
```

2. Create `models.py` with SQLAlchemy ORM tables:

```python
class User(Base):
    __tablename__ = "users"
    id         : Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email      : Mapped[str]       = mapped_column(unique=True)
    riot_puuid : Mapped[str | None]= mapped_column(unique=True, nullable=True)
    riot_id    : Mapped[str | None]= mapped_column(nullable=True)
    is_paid    : Mapped[bool]      = mapped_column(default=False)
    credits_used: Mapped[int]      = mapped_column(default=0)
    created_at : Mapped[datetime]  = mapped_column(default=datetime.utcnow)

class MagicToken(Base):
    __tablename__ = "magic_tokens"
    token      : Mapped[str]       = mapped_column(primary_key=True)
    user_id    : Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    expires_at : Mapped[datetime]
    used       : Mapped[bool]      = mapped_column(default=False)

class Report(Base):
    __tablename__ = "reports"
    id           : Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id      : Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    riot_id      : Mapped[str]
    status       : Mapped[str]       = mapped_column(default="queued")
    riot_report  : Mapped[dict | None] = mapped_column(JSON, nullable=True)
    cv_report    : Mapped[dict | None] = mapped_column(JSON, nullable=True)
    coaching     : Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None]  = mapped_column(nullable=True)
    created_at   : Mapped[datetime]    = mapped_column(default=datetime.utcnow)
    completed_at : Mapped[datetime | None] = mapped_column(nullable=True)
```

3. Replace `store.InMemoryStore` usage in `main.py` with async DB calls.
4. Run `alembic init alembic` and create the initial migration.

---

### Task B: Auth — magic link + JWT

**Complexity: Medium-High. Requires: RESEND_API_KEY, JWT_SECRET**

Create `auth.py`:

```python
# Magic link creation
async def create_magic_link(email: str, db: AsyncSession) -> str:
    # 1. Get or create User by email
    # 2. Create MagicToken (secrets.token_hex(32), expires in 15 min)
    # 3. Send email via Resend:
    import resend
    resend.api_key = RESEND_API_KEY
    resend.Emails.send({
        "from": EMAIL_FROM,
        "to": email,
        "subject": "Your login link",
        "html": f'<a href="{MAGIC_LINK_URL}?token={token}">Log in</a>'
    })
    return token

# Token verification → JWT cookie
async def verify_token(token: str, db: AsyncSession) -> str:
    # 1. Look up MagicToken — 404 if not found
    # 2. Check not used, not expired
    # 3. Mark as used
    # 4. Create JWT: {"user_id": str(user.id), "exp": now + 7 days}
    # 5. Return JWT string

# FastAPI dependency
async def get_current_user(request: Request, db: AsyncSession) -> User | None:
    token = request.cookies.get("auth_token")
    if not token: return None
    payload = jose.jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    return await db.get(User, uuid.UUID(payload["user_id"]))
```

Wire into `main.py`:
- `POST /api/v1/auth/magic-link` → `create_magic_link`
- `GET /api/v1/auth/verify?token=xxx` → `verify_token` → set httpOnly cookie → redirect to `/`
- `POST /api/v1/auth/riot-id` → require auth, validate Riot ID via `get_riot_report`, save to user

---

### Task C: Rate limiting

**Complexity: Low**

```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/analyze")
@limiter.limit("10/minute")
async def submit_analysis(...):
    ...
```

---

### Task D: Credit tracking (free tier enforcement)

**Complexity: Low — depends on Task A (DB)**

In `submit_analysis`:
```python
if user and not user.is_paid:
    if user.credits_used >= 10:
        raise HTTPException(429, "Free tier limit reached (10/month). Upgrade to continue.")
    await db.execute(update(User).where(User.id == user.id).values(credits_used=User.credits_used + 1))
```

Reset credits monthly via a cron job or on first request of new month.

---

## Done criteria
- `uvicorn services.api.main:app --reload` starts, `/health` returns 200
- `POST /api/v1/analyze` with real Riot ID returns a `done` report (needs RIOT_API_KEY + ANTHROPIC_API_KEY)
- Auth endpoints return real responses (not 501)
- `pytest services/api/tests/` passes
