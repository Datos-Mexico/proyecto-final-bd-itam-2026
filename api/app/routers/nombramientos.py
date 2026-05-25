from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_admin
from app.database import get_session
from app.models.catalogs import (
    CatNivelSalarial,
    CatPuesto,
    CatSector,
    CatTipoContratacion,
    CatTipoNomina,
    CatTipoPersonal,
    CatUniverso,
)
from app.models.servidores import Nombramiento, Persona
from app.models.users import User
from app.rate_limit import limiter
from app.schemas.errors import HTTPError401, HTTPError403, HTTPError404, HTTPError429
from app.schemas.nombramientos import NombramientoCreate, NombramientoResponse, NombramientoUpdate
from app.schemas.pagination import PaginatedResponse

router = APIRouter(prefix="/api/v1/nombramientos", tags=["nombramientos"])

# FK validation map: field_name → model
FK_MODELS = {
    "puesto_id": CatPuesto,
    "sector_id": CatSector,
    "tipo_nomina_id": CatTipoNomina,
    "tipo_contratacion_id": CatTipoContratacion,
    "tipo_personal_id": CatTipoPersonal,
    "universo_id": CatUniverso,
    "nivel_salarial_id": CatNivelSalarial,
}


async def _validate_fks(session: AsyncSession, data: dict):
    """Validate that all FK references exist."""
    for field, model in FK_MODELS.items():
        value = data.get(field)
        if value is not None:
            obj = await session.get(model, value)
            if obj is None:
                raise HTTPException(status_code=422, detail=f"{field} {value} does not exist")


_NOMB_EXAMPLE = {
    "id": 12345,
    "persona_id": 42,
    "puesto_id": 1024,
    "sector_id": 8,
    "tipo_nomina_id": 8,
    "tipo_contratacion_id": 1,
    "tipo_personal_id": 2,
    "universo_id": 3,
    "nivel_salarial_id": 11,
    "fecha_ingreso": "2015-03-12",
    "sueldo_bruto": "18500.00",
    "sueldo_neto": "14820.50",
}

_INTERNAL_NOTE = (
    "Requiere JWT admin. El SDK Python `datos-mexico` no expone este "
    "endpoint por ser operacional, no analítico."
)


@router.get(
    "/",
    response_model=PaginatedResponse[NombramientoResponse],
    summary="Listar nombramientos con paginación y filtros",
    description=(
        "[Uso interno administrativo] Lista paginada de nombramientos. "
        "Soporta filtros por `persona_id` y `sector_id`. " + _INTERNAL_NOTE
    ),
    responses={
        200: {
            "description": "Página de nombramientos.",
            "content": {
                "application/json": {
                    "example": {
                        "data": [_NOMB_EXAMPLE],
                        "total": 246821,
                        "page": 1,
                        "per_page": 50,
                        "pages": 4937,
                    }
                }
            },
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (30 req/min por IP)."},
    },
)
@limiter.limit("30/minute")
async def list_nombramientos(
    request: Request,
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    persona_id: int | None = Query(None),
    sector_id: int | None = Query(None),
):
    base = select(Nombramiento)
    count_base = select(func.count(Nombramiento.id))

    if persona_id is not None:
        base = base.where(Nombramiento.persona_id == persona_id)
        count_base = count_base.where(Nombramiento.persona_id == persona_id)
    if sector_id is not None:
        base = base.where(Nombramiento.sector_id == sector_id)
        count_base = count_base.where(Nombramiento.sector_id == sector_id)

    total = (await session.execute(count_base)).scalar_one()
    stmt = base.order_by(Nombramiento.id).offset((page - 1) * per_page).limit(per_page)
    result = await session.execute(stmt)
    data = [NombramientoResponse.model_validate(r, from_attributes=True) for r in result.scalars().all()]

    return PaginatedResponse(
        data=data, total=total, page=page, per_page=per_page,
        pages=(total + per_page - 1) // per_page if total > 0 else 0,
    )


@router.get(
    "/{nombramiento_id}",
    response_model=NombramientoResponse,
    summary="Detalle de un nombramiento por ID",
    description=(
        "[Uso interno administrativo] Detalle de un nombramiento por su "
        "ID numérico. " + _INTERNAL_NOTE
    ),
    responses={
        200: {
            "description": "Detalle de nombramiento.",
            "content": {"application/json": {"example": _NOMB_EXAMPLE}},
        },
        404: {
            "model": HTTPError404,
            "description": "`nombramiento_id` no existe.",
            "content": {"application/json": {"example": {"detail": "Nombramiento no encontrado"}}},
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (60 req/min por IP)."},
    },
)
@limiter.limit("60/minute")
async def get_nombramiento(
    request: Request,
    nombramiento_id: int,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Nombramiento).where(Nombramiento.id == nombramiento_id))
    nombramiento = result.scalar_one_or_none()
    if nombramiento is None:
        raise HTTPException(status_code=404, detail="Nombramiento no encontrado")
    return nombramiento


@router.post(
    "/",
    response_model=NombramientoResponse,
    status_code=201,
    summary="Crear un nombramiento (admin)",
    description=(
        "[Uso interno administrativo] Inserta un nombramiento nuevo "
        "asociado a una `persona_id`. Valida que la persona exista y "
        "que todos los IDs de catálogo (`puesto_id`, `sector_id`, etc.) "
        "referenciados existan. " + _INTERNAL_NOTE
    ),
    responses={
        201: {
            "description": "Nombramiento creado.",
            "content": {"application/json": {"example": _NOMB_EXAMPLE}},
        },
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        422: {"description": "`persona_id` o algún `*_id` de catálogo no existe."},
    },
)
async def create_nombramiento(
    body: NombramientoCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    # Validate persona exists
    persona = await session.get(Persona, body.persona_id)
    if persona is None:
        raise HTTPException(status_code=422, detail=f"persona_id {body.persona_id} does not exist")

    await _validate_fks(session, body.model_dump())

    nombramiento = Nombramiento(**body.model_dump())
    session.add(nombramiento)
    await session.commit()
    await session.refresh(nombramiento)
    return nombramiento


@router.put(
    "/{nombramiento_id}",
    response_model=NombramientoResponse,
    summary="Actualizar un nombramiento (admin)",
    description=(
        "[Uso interno administrativo] Actualiza campos de un nombramiento "
        "existente. Sólo los campos enviados se modifican "
        "(`exclude_unset=True`). Valida FKs referenciadas. " + _INTERNAL_NOTE
    ),
    responses={
        200: {
            "description": "Nombramiento actualizado.",
            "content": {"application/json": {"example": _NOMB_EXAMPLE}},
        },
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        404: {
            "model": HTTPError404,
            "description": "`nombramiento_id` no existe.",
            "content": {"application/json": {"example": {"detail": "Nombramiento no encontrado"}}},
        },
        422: {"description": "Algún `*_id` de catálogo en el body no existe."},
    },
)
async def update_nombramiento(
    nombramiento_id: int,
    body: NombramientoUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    nombramiento = await session.get(Nombramiento, nombramiento_id)
    if nombramiento is None:
        raise HTTPException(status_code=404, detail="Nombramiento no encontrado")

    update_data = body.model_dump(exclude_unset=True)
    await _validate_fks(session, update_data)

    for key, value in update_data.items():
        setattr(nombramiento, key, value)

    session.add(nombramiento)
    await session.commit()
    await session.refresh(nombramiento)
    return nombramiento


@router.delete(
    "/{nombramiento_id}",
    status_code=204,
    summary="Eliminar un nombramiento (admin)",
    description=(
        "[Uso interno administrativo] Elimina un nombramiento existente. "
        "No tiene constraint FK de cascada — la persona padre permanece. "
        + _INTERNAL_NOTE
    ),
    responses={
        204: {"description": "Nombramiento eliminado (sin body)."},
        401: {"model": HTTPError401, "description": "JWT ausente o inválido."},
        403: {"model": HTTPError403, "description": "Usuario autenticado sin privilegios admin."},
        404: {
            "model": HTTPError404,
            "description": "`nombramiento_id` no existe.",
            "content": {"application/json": {"example": {"detail": "Nombramiento no encontrado"}}},
        },
    },
)
async def delete_nombramiento(
    nombramiento_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    nombramiento = await session.get(Nombramiento, nombramiento_id)
    if nombramiento is None:
        raise HTTPException(status_code=404, detail="Nombramiento no encontrado")

    await session.delete(nombramiento)
    await session.commit()
