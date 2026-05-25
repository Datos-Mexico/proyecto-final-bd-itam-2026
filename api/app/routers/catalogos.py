from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from sqlalchemy import cast, func, select, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_session
from app.models.users import User
from app.rate_limit import limiter
from app.models.catalogs import (
    CatNivelSalarial,
    CatPuesto,
    CatSector,
    CatSexo,
    CatTipoContratacion,
    CatTipoNomina,
    CatTipoPersonal,
    CatUniverso,
)
from app.models.servidores import Nombramiento, Persona
from app.schemas.catalogs import CatalogItemWithCount, PuestoWithCount
from app.schemas.errors import HTTPError401, HTTPError403, HTTPError404, HTTPError409, HTTPError429
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/catalogos", tags=["catalogos"])

# --- Catalog metadata for generic CRUD ---
CATALOG_MAP: dict[str, dict[str, Any]] = {
    "sexos": {
        "model": CatSexo,
        "fk_col": Persona.sexo_id,
        "fields": ["nombre"],
    },
    "puestos": {
        "model": CatPuesto,
        "fk_col": Nombramiento.puesto_id,
        "fields": ["nombre"],
    },
    "tipos-contratacion": {
        "model": CatTipoContratacion,
        "fk_col": Nombramiento.tipo_contratacion_id,
        "fields": ["nombre"],
    },
    "tipos-personal": {
        "model": CatTipoPersonal,
        "fk_col": Nombramiento.tipo_personal_id,
        "fields": ["nombre"],
    },
    "tipos-nomina": {
        "model": CatTipoNomina,
        "fk_col": Nombramiento.tipo_nomina_id,
        "fields": ["clave"],
    },
    "universos": {
        "model": CatUniverso,
        "fk_col": Nombramiento.universo_id,
        "fields": ["clave", "nombre"],
    },
    "sectores": {
        "model": CatSector,
        "fk_col": Nombramiento.sector_id,
        "fields": ["clave", "nombre"],
    },
    "niveles-salariales": {
        "model": CatNivelSalarial,
        "fk_col": Nombramiento.nivel_salarial_id,
        "fields": ["clave"],
    },
}


def _get_catalog(tipo: str):
    info = CATALOG_MAP.get(tipo)
    if info is None:
        raise HTTPException(status_code=404, detail=f"Catalog type '{tipo}' not found")
    return info


def _item_to_dict(item) -> dict:
    return {"id": item.id, **{c.name: getattr(item, c.name) for c in item.__table__.columns if c.name != "id"}}


# ============ Existing GET endpoints ============

async def _catalog_with_count(session: AsyncSession, model, fk_col):
    stmt = (
        select(model.id, model.nombre, func.count(Nombramiento.id).label("count"))
        .outerjoin(Nombramiento, fk_col == model.id)
        .group_by(model.id, model.nombre)
        .order_by(model.nombre)
    )
    result = await session.execute(stmt)
    return [CatalogItemWithCount(id=r.id, nombre=r.nombre, count=r.count) for r in result.all()]


_CATALOG_EXAMPLE = [
    {"id": 1, "nombre": "Base", "count": 153000},
    {"id": 2, "nombre": "Honorarios", "count": 28400},
]

_INTERNAL_NOTE = (
    "Requiere JWT admin. El SDK Python `datos-mexico` no expone este "
    "endpoint por ser operacional, no analítico."
)

_RESP_429 = {"model": HTTPError429, "description": "Rate limit excedido (60 req/min por IP)."}
_RESP_200_CATALOG = {
    "description": "Lista del catálogo con conteo de uso.",
    "content": {"application/json": {"example": _CATALOG_EXAMPLE}},
}


@router.get(
    "/tipos-contratacion",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de tipos de contratación con conteo de uso",
    description=(
        "Devuelve los tipos de contratación del padrón CDMX (Base, Honorarios, "
        "Eventual, etc.) con el conteo de nombramientos que referencian cada uno. "
        "Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def tipos_contratacion(request: Request, session: AsyncSession = Depends(get_session)):
    return await _catalog_with_count(session, CatTipoContratacion, Nombramiento.tipo_contratacion_id)


@router.get(
    "/tipos-personal",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de tipos de personal con conteo de uso",
    description=(
        "Devuelve los tipos de personal (Operativo, Mando, etc.) con conteo de "
        "nombramientos por tipo. Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def tipos_personal(request: Request, session: AsyncSession = Depends(get_session)):
    return await _catalog_with_count(session, CatTipoPersonal, Nombramiento.tipo_personal_id)


@router.get(
    "/tipos-nomina",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de tipos de nómina con conteo de uso",
    description=(
        "Devuelve los tipos de nómina identificados por la columna `clave` "
        "(integer, NO `nombre` como los otros catálogos) con conteo de uso. "
        "Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def tipos_nomina(request: Request, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            CatTipoNomina.id,
            cast(CatTipoNomina.clave, String).label("nombre"),
            func.count(Nombramiento.id).label("count"),
        )
        .outerjoin(Nombramiento, Nombramiento.tipo_nomina_id == CatTipoNomina.id)
        .group_by(CatTipoNomina.id, CatTipoNomina.clave)
        .order_by(CatTipoNomina.clave)
    )
    result = await session.execute(stmt)
    return [CatalogItemWithCount(id=r.id, nombre=r.nombre, count=r.count) for r in result.all()]


@router.get(
    "/universos",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de universos con conteo de uso",
    description=(
        "Devuelve los universos del padrón CDMX (agrupaciones administrativas) "
        "con conteo de nombramientos por universo. Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def universos(request: Request, session: AsyncSession = Depends(get_session)):
    return await _catalog_with_count(session, CatUniverso, Nombramiento.universo_id)


@router.get(
    "/sectores",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de los 73 sectores con conteo de uso",
    description=(
        "Devuelve los 73 sectores del padrón CDMX con conteo de nombramientos "
        "por sector, ordenados alfabéticamente. Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def sectores(request: Request, session: AsyncSession = Depends(get_session)):
    return await _catalog_with_count(session, CatSector, Nombramiento.sector_id)


@router.get(
    "/sexos",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de sexos con conteo de uso",
    description=(
        "Devuelve el catálogo `cat_sexos` (MASCULINO, FEMENINO, no especificado) "
        "con conteo de personas por valor. Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def sexos(request: Request, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(CatSexo.id, CatSexo.nombre, func.count(Persona.id).label("count"))
        .outerjoin(Persona, Persona.sexo_id == CatSexo.id)
        .group_by(CatSexo.id, CatSexo.nombre)
        .order_by(CatSexo.nombre)
    )
    result = await session.execute(stmt)
    return [CatalogItemWithCount(id=r.id, nombre=r.nombre, count=r.count) for r in result.all()]


@router.get(
    "/niveles-salariales",
    response_model=list[CatalogItemWithCount],
    summary="Catálogo de niveles salariales con conteo de uso",
    description=(
        "Devuelve los niveles salariales identificados por `clave` con conteo "
        "de nombramientos por nivel. Cache HTTP `public, max-age=3600`."
    ),
    responses={200: _RESP_200_CATALOG, 429: _RESP_429},
)
@limiter.limit("60/minute")
async def niveles_salariales(request: Request, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(
            CatNivelSalarial.id,
            cast(CatNivelSalarial.clave, String).label("nombre"),
            func.count(Nombramiento.id).label("count"),
        )
        .outerjoin(Nombramiento, Nombramiento.nivel_salarial_id == CatNivelSalarial.id)
        .group_by(CatNivelSalarial.id, CatNivelSalarial.clave)
        .order_by(CatNivelSalarial.clave)
    )
    result = await session.execute(stmt)
    return [CatalogItemWithCount(id=r.id, nombre=r.nombre, count=r.count) for r in result.all()]


@router.get(
    "/puestos",
    response_model=PaginatedResponse[PuestoWithCount],
    summary="Catálogo paginado de puestos con búsqueda",
    description=(
        "Devuelve los 1 772 puestos del padrón CDMX paginados, con conteo "
        "de nombramientos por puesto. Soporta búsqueda ILIKE vía `search`. "
        "Ordenado por conteo descendente. Cache HTTP `public, max-age=3600`."
    ),
    responses={
        200: {
            "description": "Página del catálogo de puestos.",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {"id": 1024, "nombre": "POLICIA", "count": 80000},
                            {"id": 1025, "nombre": "DOCENTE FRENTE A GRUPO", "count": 12500},
                        ],
                        "total": 1772,
                        "page": 1,
                        "per_page": 50,
                        "pages": 36,
                    }
                }
            },
        },
        429: _RESP_429,
    },
)
@limiter.limit("60/minute")
async def puestos(
    request: Request,
    session: AsyncSession = Depends(get_session),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
):
    base = (
        select(CatPuesto.id, CatPuesto.nombre, func.count(Nombramiento.id).label("count"))
        .outerjoin(Nombramiento, Nombramiento.puesto_id == CatPuesto.id)
        .group_by(CatPuesto.id, CatPuesto.nombre)
    )
    if search:
        base = base.where(CatPuesto.nombre.ilike(f"%{search}%"))

    count_stmt = select(func.count()).select_from(
        select(CatPuesto.id).where(CatPuesto.nombre.ilike(f"%{search}%")).subquery()
        if search
        else select(CatPuesto.id).subquery()
    )
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = base.order_by(func.count(Nombramiento.id).desc()).offset((page - 1) * per_page).limit(per_page)
    result = await session.execute(stmt)
    data = [PuestoWithCount(id=r.id, nombre=r.nombre, count=r.count) for r in result.all()]

    return PaginatedResponse(
        data=data, total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


# ============ Generic CRUD: POST / PUT / DELETE ============

_CATALOG_TIPOS = "`sexos`, `puestos`, `tipos-contratacion`, `tipos-personal`, `tipos-nomina`, `universos`, `sectores`, `niveles-salariales`"


@router.post(
    "/{tipo}",
    status_code=201,
    summary="Crear un item en un catálogo (admin)",
    description=(
        "[Uso interno administrativo] Inserta un item nuevo en uno de los "
        f"catálogos: {_CATALOG_TIPOS}. Cada catálogo tiene su lista de "
        "campos requeridos (`nombre`, `clave`, o combinación). "
        + _INTERNAL_NOTE
    ),
    responses={
        201: {"description": "Item de catálogo creado."},
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        404: {
            "model": HTTPError404,
            "description": "El `tipo` de catálogo no existe (debe ser uno de los 8 listados).",
            "content": {"application/json": {"example": {"detail": "Catalog type 'foo' not found"}}},
        },
        422: {"description": "Campo requerido del catálogo ausente en el body."},
    },
)
async def create_catalog_item(
    tipo: str,
    body: dict = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    info = _get_catalog(tipo)
    model = info["model"]
    required_fields = info["fields"]

    # Validate required fields
    for field in required_fields:
        if field not in body:
            raise HTTPException(status_code=422, detail=f"Missing required field: '{field}'")

    kwargs = {f: body[f] for f in required_fields}
    item = model(**kwargs)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _item_to_dict(item)


@router.put(
    "/{tipo}/{item_id}",
    summary="Actualizar un item de catálogo (admin)",
    description=(
        "[Uso interno administrativo] Actualiza un item existente en uno "
        f"de los catálogos ({_CATALOG_TIPOS}). Sólo los campos válidos para "
        "ese catálogo son aplicados. " + _INTERNAL_NOTE
    ),
    responses={
        200: {"description": "Item actualizado."},
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        404: {
            "model": HTTPError404,
            "description": "`tipo` de catálogo o `item_id` no existe.",
            "content": {"application/json": {"example": {"detail": "sectores item 999 not found"}}},
        },
    },
)
async def update_catalog_item(
    tipo: str,
    item_id: int,
    body: dict = Body(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    info = _get_catalog(tipo)
    model = info["model"]
    allowed_fields = info["fields"]

    item = await session.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{tipo} item {item_id} not found")

    for field in allowed_fields:
        if field in body:
            setattr(item, field, body[field])

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return _item_to_dict(item)


@router.delete(
    "/{tipo}/{item_id}",
    status_code=204,
    summary="Eliminar un item de catálogo (admin) — bloqueado si hay FK refs",
    description=(
        "[Uso interno administrativo] Elimina un item de catálogo. "
        "**Devuelve 409 si hay nombramientos o personas que referencian este "
        "item** — primero hay que migrarlos o eliminarlos. " + _INTERNAL_NOTE
    ),
    responses={
        204: {"description": "Item eliminado (sin body)."},
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        404: {
            "model": HTTPError404,
            "description": "`tipo` o `item_id` no existe.",
            "content": {"application/json": {"example": {"detail": "puestos item 999 not found"}}},
        },
        409: {
            "model": HTTPError409,
            "description": "El item tiene FK refs activas (no se puede borrar).",
            "content": {"application/json": {"example": {"detail": "Cannot delete: 80000 records reference this puestos item"}}},
        },
    },
)
async def delete_catalog_item(
    tipo: str,
    item_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    info = _get_catalog(tipo)
    model = info["model"]
    fk_col = info["fk_col"]

    item = await session.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{tipo} item {item_id} not found")

    count_result = await session.execute(
        select(func.count()).where(fk_col == item_id)
    )
    ref_count = count_result.scalar_one()
    if ref_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete: {ref_count} records reference this {tipo} item",
        )

    await session.delete(item)
    await session.commit()
