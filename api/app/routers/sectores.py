from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.rate_limit import limiter
from app.schemas.errors import HTTPError404, HTTPError429
from app.schemas.sectores import SectorComparison, SectorDetailStats, SectorWithStats, TopPuesto

router = APIRouter(prefix="/api/v1/sectores", tags=["sectores"])


@router.get(
    "/",
    response_model=list[SectorWithStats],
    summary="Listar los 73 sectores del padrón CDMX con estadísticas",
    description=(
        "Devuelve los 73 sectores con conteo de nombramientos, sueldo bruto "
        "promedio, y desglose hombres/mujeres por sector. Ordenado "
        "alfabéticamente. Cache HTTP `public, max-age=3600`."
    ),
    responses={
        200: {
            "description": "Lista de sectores con stats agregadas.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "nombre": "Secretaría de Educación",
                            "total_servidores": 8230,
                            "sueldo_bruto_avg": 14820.50,
                            "count_hombres": 3100,
                            "count_mujeres": 5130,
                        }
                    ]
                }
            },
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (30 req/min por IP)."},
    },
)
@limiter.limit("30/minute")
async def list_sectores(request: Request, session: AsyncSession = Depends(get_session)):
    sql = """
    SELECT
        cs.id, cs.nombre,
        COUNT(n.id) AS total_servidores,
        AVG(n.sueldo_bruto)::float AS sueldo_bruto_avg,
        COUNT(*) FILTER (WHERE csex.nombre = 'MASCULINO') AS count_hombres,
        COUNT(*) FILTER (WHERE csex.nombre = 'FEMENINO') AS count_mujeres
    FROM cdmx.cat_sectores cs
    LEFT JOIN cdmx.nombramientos n ON n.sector_id = cs.id
    LEFT JOIN cdmx.personas p ON n.persona_id = p.id
    LEFT JOIN cdmx.cat_sexos csex ON p.sexo_id = csex.id
    GROUP BY cs.id, cs.nombre
    ORDER BY cs.nombre
    """
    result = await session.execute(text(sql))
    return [
        SectorWithStats(
            id=r["id"], nombre=r["nombre"],
            total_servidores=r["total_servidores"],
            sueldo_bruto_avg=r["sueldo_bruto_avg"],
            count_hombres=r["count_hombres"],
            count_mujeres=r["count_mujeres"],
        )
        for r in result.mappings().all()
    ]


async def _sector_detail(session: AsyncSession, sector_id: int) -> SectorDetailStats:
    sql = """
    SELECT
        cs.id, cs.nombre,
        COUNT(n.id) AS total_servidores,
        AVG(n.sueldo_bruto)::float AS sueldo_bruto_avg,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY n.sueldo_bruto)::float AS sueldo_bruto_median,
        AVG(n.sueldo_neto)::float AS sueldo_neto_avg,
        AVG(p.edad)::float AS edad_avg,
        COUNT(*) FILTER (WHERE csex.nombre = 'MASCULINO') AS count_hombres,
        COUNT(*) FILTER (WHERE csex.nombre = 'FEMENINO') AS count_mujeres,
        CASE
            WHEN AVG(n.sueldo_bruto) FILTER (WHERE csex.nombre = 'FEMENINO') > 0
            THEN ((AVG(n.sueldo_bruto) FILTER (WHERE csex.nombre = 'MASCULINO')
                  - AVG(n.sueldo_bruto) FILTER (WHERE csex.nombre = 'FEMENINO'))
                  / AVG(n.sueldo_bruto) FILTER (WHERE csex.nombre = 'FEMENINO') * 100)::float
            ELSE NULL
        END AS brecha_genero_pct
    FROM cdmx.cat_sectores cs
    LEFT JOIN cdmx.nombramientos n ON n.sector_id = cs.id
    LEFT JOIN cdmx.personas p ON n.persona_id = p.id
    LEFT JOIN cdmx.cat_sexos csex ON p.sexo_id = csex.id
    WHERE cs.id = :sector_id
    GROUP BY cs.id, cs.nombre
    """
    result = await session.execute(text(sql), {"sector_id": sector_id})
    row = result.mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Sector no encontrado")

    # Top puestos
    puestos_sql = """
    SELECT cp.nombre AS puesto, COUNT(*) AS count, AVG(n.sueldo_bruto)::float AS sueldo_avg
    FROM cdmx.nombramientos n
    JOIN cdmx.cat_puestos cp ON n.puesto_id = cp.id
    WHERE n.sector_id = :sector_id
    GROUP BY cp.nombre
    ORDER BY count DESC
    LIMIT 10
    """
    puestos_result = await session.execute(text(puestos_sql), {"sector_id": sector_id})
    top_puestos = [
        TopPuesto(puesto=r["puesto"], count=r["count"], sueldo_avg=r["sueldo_avg"])
        for r in puestos_result.mappings().all()
    ]

    return SectorDetailStats(
        id=row["id"], nombre=row["nombre"],
        total_servidores=row["total_servidores"],
        sueldo_bruto_avg=row["sueldo_bruto_avg"],
        sueldo_bruto_median=row["sueldo_bruto_median"],
        sueldo_neto_avg=row["sueldo_neto_avg"],
        edad_avg=row["edad_avg"],
        count_hombres=row["count_hombres"],
        count_mujeres=row["count_mujeres"],
        brecha_genero_pct=row["brecha_genero_pct"],
        top_puestos=top_puestos,
    )


@router.get(
    "/compare",
    response_model=SectorComparison,
    summary="Comparar dos sectores lado a lado",
    description=(
        "Devuelve el detalle estadístico completo (sueldo promedio, "
        "mediana, percentiles, top 10 puestos, brecha de género) para "
        "dos sectores identificados por su `id`. Útil para visualizaciones "
        "comparativas. Si cualquiera de los dos sectores no existe, "
        "devuelve `404` (el primer raise gana — `a` antes que `b`). "
        "Cache HTTP `public, max-age=3600`."
    ),
    responses={
        200: {"description": "Comparación lado a lado de dos sectores."},
        404: {
            "model": HTTPError404,
            "description": "Uno o ambos `sector_id` no existen en `cdmx.cat_sectores`.",
            "content": {"application/json": {"example": {"detail": "Sector no encontrado"}}},
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (15 req/min por IP)."},
    },
)
@limiter.limit("15/minute")
async def compare_sectores(
    request: Request,
    a: int = Query(..., description="ID del sector A"),
    b: int = Query(..., description="ID del sector B"),
    session: AsyncSession = Depends(get_session),
):
    sector_a = await _sector_detail(session, a)
    sector_b = await _sector_detail(session, b)
    return SectorComparison(sector_a=sector_a, sector_b=sector_b)


@router.get(
    "/{sector_id}/stats",
    response_model=SectorDetailStats,
    summary="Detalle estadístico de un sector",
    description=(
        "Detalle completo de un sector identificado por `sector_id`: "
        "totales, promedio y mediana de sueldo bruto, percentiles, "
        "promedio de edad, desglose por género (con brecha %), y top 10 "
        "puestos del sector con su sueldo promedio. Cache HTTP "
        "`public, max-age=3600`."
    ),
    responses={
        200: {
            "description": "Detalle completo del sector.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "nombre": "Secretaría de Educación",
                        "total_servidores": 8230,
                        "sueldo_bruto_avg": 14820.50,
                        "sueldo_bruto_median": 12500.00,
                        "sueldo_neto_avg": 12200.30,
                        "edad_avg": 38.5,
                        "count_hombres": 3100,
                        "count_mujeres": 5130,
                        "brecha_genero_pct": 12.4,
                        "top_puestos": [
                            {"puesto": "DOCENTE", "count": 4200, "sueldo_avg": 13200.0}
                        ],
                    }
                }
            },
        },
        404: {
            "model": HTTPError404,
            "description": "`sector_id` no existe en `cdmx.cat_sectores`.",
            "content": {"application/json": {"example": {"detail": "Sector no encontrado"}}},
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (30 req/min por IP)."},
    },
)
@limiter.limit("30/minute")
async def sector_stats(
    request: Request,
    sector_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await _sector_detail(session, sector_id)
