# Etapa 5 — APIs REST con FastAPI

## Resumen ejecutivo

Esta etapa expone el esquema normalizado 4NF de la Etapa 3 a través
de una API REST construida con FastAPI. La API permite consultar
el padrón programáticamente, ofrece endpoints analíticos
pre-computados, y sirve como capa de acceso para el SDK Python
y el sitio canónico del Observatorio Datos México.

El código completo está en [`api/`](../api/) y consta de:

- 1 entry point (`api/main.py`)
- 7 módulos core en `api/app/` (config, database, auth, dependencies,
  rate_limit, main, __init__)
- 4 modelos ORM SQLModel en `api/app/models/`
- 8 routers en `api/app/routers/` (auth, servidores, sectores,
  catalogos, dashboard, analytics, personas, nombramientos)
- 11 schemas Pydantic en `api/app/schemas/`
- 7 migraciones SQL en `api/migrations/` (alineadas con los scripts
  académicos de `sql/`)
- 13 archivos de tests en `api/tests/`

## Endpoints expuestos

| Prefix | Descripción | Endpoints clave |
|---|---|---|
| `/api/v1/auth` | Autenticación JWT | `POST /token`, `GET /me`, (`/register` deshabilitado intencionalmente) |
| `/api/v1/servidores` | Consulta del padrón | `GET /` con filtros, `GET /stats`, `GET /{id}` |
| `/api/v1/sectores` | Sectores de gobierno | `GET /`, `GET /compare`, `GET /{id}/stats` |
| `/api/v1/personas` | CRUD personas | `GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}` |
| `/api/v1/nombramientos` | CRUD nombramientos | análogo |
| `/api/v1/catalogos` | 8 catálogos | `GET /sexos`, `GET /puestos`, `GET /sectores`, etc. + CRUD genérico |
| `/api/v1/dashboard` | Agregaciones dashboard | `GET /stats` (campo a campo de las estadísticas globales) |
| `/api/v1/analytics` | Analíticas avanzadas | `GET /brecha-edad`, `GET /puestos/ranking`, `GET /sectores/ranking` |
| `/health` | Liveness probe | `GET` |

La especificación OpenAPI completa se autogenera con FastAPI y
queda disponible en `http://localhost:8000/openapi.json` cuando el
servidor está corriendo, además del UI interactivo Swagger en
`http://localhost:8000/docs`.

## Setup local

### Requisitos

- Python ≥ 3.13
- [`uv`](https://github.com/astral-sh/uv)
- PostgreSQL ≥ 16

### Pasos

```bash
# 1. Levantar Postgres local y crear base
createdb proyecto_academico

# 2. Aplicar migraciones (en orden)
cd api/
psql $DATABASE_URL -f migrations/001_normalize.sql      # — NO; ver nota abajo
psql $DATABASE_URL -f migrations/002_users.sql
psql $DATABASE_URL -f migrations/003_indexes_and_extensions.sql
psql $DATABASE_URL -f migrations/004_materialized_views.sql
psql $DATABASE_URL -f migrations/005_multischema_cdmx.sql
psql $DATABASE_URL -f migrations/008_users_is_admin.sql
```

**Nota sobre la migración 001**: si la base ya viene del flujo
académico (`sql/01-staging/*` + `sql/04-migracion/*`), la
normalización ya está aplicada y `migrations/001_normalize.sql` se
omite. Si se carga la base desde el dump físico raw, se aplica la
migración 001 para completar la normalización.

```bash
# 3. Configurar variables
cp .env.example .env
# Editar .env con el DATABASE_URL correcto.

# 4. Instalar dependencies
uv sync

# 5. Arrancar la API
uv run uvicorn app.main:app --reload --port 8000

# 6. Abrir Swagger UI
open http://localhost:8000/docs
```

## Ejemplos de uso

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

### Estadísticas del dashboard

```bash
curl -s http://localhost:8000/api/v1/dashboard/stats | jq '{
  totalServidores,
  totalSectors,
  avgSalary,
  medianSalary,
  genderGapPercent
}'
```

Respuesta (con datos del dump):

```json
{
  "totalServidores": 246821,
  "totalSectors": 73,
  "avgSalary": 13225.32,
  "medianSalary": 10410.00,
  "genderGapPercent": 3.76
}
```

### Catálogo de sectores

```bash
curl -s "http://localhost:8000/api/v1/catalogos/sectores?limit=5" | jq .
```

### Servidor por id

```bash
curl -s http://localhost:8000/api/v1/servidores/1 | jq .
```

### Ranking de sectores por brecha

```bash
curl -s "http://localhost:8000/api/v1/analytics/sectores/ranking?min_n=100&order_by=brecha_pct" | jq '.[0:5]'
```

### Autenticación

```bash
# Registrar (deshabilitado intencionalmente en este snapshot)
curl -X POST http://localhost:8000/api/v1/auth/token \
  -d "username=admin&password=PLACEHOLDER"
```

## Stack técnico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Framework HTTP | FastAPI ≥ 0.115 |
| ORM | SQLModel + SQLAlchemy[asyncio] ≥ 2.0 |
| Driver DB | asyncpg ≥ 0.30 |
| Settings | pydantic-settings ≥ 2.7 |
| Auth | python-jose (JWT HS256) + bcrypt |
| Rate limiting | slowapi |
| Tests | pytest + pytest-asyncio + httpx |
| Package manager | `uv` |

## Tests

```bash
cd api/
TESTING=1 uv run pytest -v
```

Los 13 archivos de tests cubren:
- Endpoints CRUD de personas, nombramientos, catálogos
- Autenticación (token, me)
- Dashboard stats
- Analytics
- Materialized views
- Health
- Servidores y sectores

## Caveats académicos

- El módulo `auth.py` incluye un endpoint `/register` que **lanza
  HTTP 403 intencionalmente** — el observatorio decidió que el
  registro no debe estar abierto al público. La provisión de
  usuarios admin se hace vía CLI (no incluida en este snapshot;
  ver `scripts/create_admin.py` en el backend de producción).
- El rate limiting con `slowapi` se desactiva automáticamente
  cuando `TESTING=1` está en el entorno (`api/app/rate_limit.py`).
- La autenticación con `passlib` fue evitada porque genera
  incompatibilidad con Python 3.13; se usa `bcrypt` directamente.
