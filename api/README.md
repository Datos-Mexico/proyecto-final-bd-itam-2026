# API académica — Padrón Servidores Públicos CDMX

FastAPI snapshot del backend del Observatorio Datos México para el
proyecto final de Bases de Datos COM-12101-001 (ITAM, Primavera 2026).

Esta API expone el dataset CDMX servidores públicos a través de
endpoints REST consultables localmente. Es la entrega de la **Etapa 5**
de la rúbrica del proyecto académico.

---

## Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python ≥ 3.13 |
| Framework | FastAPI ≥ 0.115 |
| ORM | SQLModel + SQLAlchemy[asyncio] |
| Driver DB | asyncpg |
| Settings | pydantic-settings |
| Auth | python-jose (JWT HS256) + bcrypt |
| Rate limiting | slowapi |
| Tests | pytest + pytest-asyncio + httpx |
| Package manager | `uv` (lockfile en `uv.lock`) |
| Base de datos | PostgreSQL ≥ 16 (local) |

## Estructura

```
api/
├── app/
│   ├── main.py              FastAPI app + middlewares + routers
│   ├── auth.py              JWT helpers + get_current_user
│   ├── config.py            Pydantic Settings (DATABASE_URL, CORS, ...)
│   ├── database.py          Async engine + get_session
│   ├── dependencies.py      Filtros y paginación
│   ├── rate_limit.py        slowapi limiter
│   ├── models/              SQLModel ORM (catalogs, servidores, users)
│   ├── routers/             8 routers (auth, servidores, sectores,
│   │                        catalogos, dashboard, analytics,
│   │                        personas, nombramientos)
│   └── schemas/             Pydantic response/request models
├── migrations/              SQL plano numerado (001 normalize, 002 users,
│                            003 indexes, 004 MVs, 005 multischema cdmx,
│                            008 users is_admin)
├── tests/                   pytest suite scope CDMX
├── Dockerfile               Build local
├── pyproject.toml           Manifest
├── uv.lock                  Lockfile reproducible
├── .env.example             Plantilla de variables
└── main.py                  Entry point (uvicorn)
```

## Endpoints expuestos (scope académico CDMX)

- `/api/v1/auth/*` — token, me (register intencionalmente deshabilitado)
- `/api/v1/servidores/*` — list, stats, by id
- `/api/v1/sectores/*` — list, compare, stats
- `/api/v1/personas/*` — CRUD
- `/api/v1/nombramientos/*` — CRUD
- `/api/v1/catalogos/*` — sexos, puestos, sectores, niveles_salariales,
  tipos_nomina, tipos_contratacion, tipos_personal, universos
- `/api/v1/dashboard/stats` — agregaciones para dashboard
- `/api/v1/analytics/*` — brecha-edad, puestos/ranking, sectores/ranking
- `/health` — liveness probe

## Cómo correr local

### Requisitos previos

- Python 3.13+
- `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- PostgreSQL 16+ local

### Setup

```bash
cd api/
cp .env.example .env
# Editar .env y completar DATABASE_URL apuntando a tu Postgres local.

uv sync                              # Instala dependencias del lockfile
uv run alembic-style apply           # (Ver migrations/ — aplicar SQL plano)

# Aplicar migraciones manualmente sobre la base local:
psql $DATABASE_URL -f migrations/001_normalize.sql
psql $DATABASE_URL -f migrations/002_users.sql
psql $DATABASE_URL -f migrations/003_indexes_and_extensions.sql
psql $DATABASE_URL -f migrations/004_materialized_views.sql
psql $DATABASE_URL -f migrations/005_multischema_cdmx.sql
psql $DATABASE_URL -f migrations/008_users_is_admin.sql

# Correr la API
uv run uvicorn app.main:app --reload --port 8000

# Abrir Swagger UI
open http://localhost:8000/docs
```

### Tests

```bash
cd api/
TESTING=1 uv run pytest -v
```

Los tests asumen una base de datos local correctamente migrada. Ver
`tests/conftest.py` para fixtures.

## Diferencias con el backend de producción

Este snapshot es **subconjunto académico** del backend completo
disponible en `api.datos-itam.org`. Diferencias intencionales:

- Solo expone endpoints del **dataset CDMX** (servidores públicos).
  Los datasets ENIGH, CONSAR, ENOE del observatorio público no están
  en este snapshot.
- No tiene endpoints administrativos (`/admin/*`), demo (`/demo/*`),
  comparativos cross-dataset (`/comparativo/*`), ni ingesta CSV
  (`/ingest/csv`).
- Servidor configurado para `http://localhost:8000`, no para
  producción.
- Sin secret real de JWT — debe configurarse localmente.

## Licencia

[MIT](../LICENSE) © 2026 David Fernando Ávila Díaz.
