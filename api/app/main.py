from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import engine
from app.rate_limit import limiter
from app.routers import analytics, auth, catalogos, dashboard, nombramientos, personas, sectores, servidores


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


API_DESCRIPTION = """
API REST del proyecto académico de Bases de Datos COM-12101-001
(ITAM, Primavera 2026).

**Dataset expuesto:**
- **Servidores públicos CDMX** (schema `cdmx`): 246K registros del Padrón
  de Servidores Públicos de la Ciudad de México (datos.gob.mx).

**Estructura del esquema normalizado (4NF):**
- 2 tablas de datos (`personas`, `nombramientos`)
- 8 catálogos (`cat_sexos`, `cat_puestos`, `cat_sectores`,
  `cat_tipos_nomina`, `cat_tipos_contratacion`, `cat_tipos_personal`,
  `cat_universos`, `cat_niveles_salariales`)
- 5 materialized views agregadas para el dashboard

**Versión académica:** este snapshot es un subconjunto del backend del
Observatorio Datos México (api.datos-itam.org) limitado al scope del
proyecto académico final. La documentación académica completa del proceso
está en el repositorio.
"""

app = FastAPI(
    title="Proyecto académico — API CDMX servidores públicos",
    description=API_DESCRIPTION,
    version="1.0.0",
    contact={
        "name": "Equipo técnico fundador",
        "email": "df.avila.diaz@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8000", "description": "Local académico"},
    ],
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*", "Authorization"],
)


WRITE_PREFIXES = ("/api/v1/auth", "/api/v1/personas", "/api/v1/nombramientos")


def _set_public_cache(response, cache_value: str) -> None:
    """Set Cache-Control and ensure Vary: Origin.

    Why Vary: Origin: CORSMiddleware only sets Access-Control-Allow-Origin
    when the request has an Origin header. If a non-browser client (curl
    without -H Origin, healthcheck, prefetcher) hits a cacheable endpoint
    first, the CDN caches the response WITHOUT the CORS header. Subsequent
    browser requests get that cached response and fail CORS. Setting
    Vary: Origin forces the CDN to key cache entries by URL + Origin so
    browser and non-browser responses don't collide.
    """
    response.headers["Cache-Control"] = cache_value
    existing_vary = response.headers.get("Vary", "")
    vary_parts = [v.strip() for v in existing_vary.split(",") if v.strip()]
    if not any(v.lower() == "origin" for v in vary_parts):
        vary_parts.append("Origin")
    response.headers["Vary"] = ", ".join(vary_parts)


class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        # Don't cache write endpoints
        if any(path.startswith(p) for p in WRITE_PREFIXES):
            response.headers["Cache-Control"] = "no-store"
        elif "/catalogos/" in path or path.startswith("/api/v1/sectores"):
            _set_public_cache(response, "public, max-age=3600")
        elif path.startswith("/api/v1/dashboard"):
            _set_public_cache(response, "public, max-age=3600")
        elif path.startswith("/api/v1/analytics"):
            _set_public_cache(response, "public, max-age=900")
        elif "/servidores/" in path:
            _set_public_cache(response, "public, max-age=300")
        return response


app.add_middleware(CacheControlMiddleware)


app.include_router(auth.router)
app.include_router(servidores.router)
app.include_router(sectores.router)
app.include_router(catalogos.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(personas.router)
app.include_router(nombramientos.router)


@app.get(
    "/health",
    tags=["meta"],
    summary="Liveness probe",
    description="Endpoint de salud del servicio. Devuelve 200 si la API está operativa.",
    responses={
        200: {
            "description": "Servicio operativo.",
            "content": {"application/json": {"example": {"status": "ok"}}},
        },
    },
)
async def health():
    return {"status": "ok"}


