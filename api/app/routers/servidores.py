from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import cast, func, select, String, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.dependencies import ServidorFilters, apply_filters, apply_ordering, get_filters
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
from app.rate_limit import limiter
from app.schemas.errors import HTTPError404, HTTPError429
from app.schemas.pagination import PaginatedResponse
from app.schemas.servidores import ServidorDetail, ServidorListItem, ServidorStats, SueldoDistribucion

router = APIRouter(prefix="/api/v1/servidores", tags=["servidores"])

P = Persona
N = Nombramiento


@router.get(
    "/",
    response_model=PaginatedResponse[ServidorListItem],
    summary="Listar servidores con filtros y paginación",
    description=(
        "Lista paginada de servidores del padrón CDMX (246K registros). "
        "Soporta filtros por `sector_id`, `sexo`, rango de edad, rango de "
        "sueldo, `tipo_contratacion_id`, `tipo_personal_id`, `universo_id`, "
        "y `puesto_search` (búsqueda ILIKE sobre el nombre del puesto). "
        "Cache HTTP `public, max-age=300`."
    ),
    responses={
        200: {
            "description": "Página de servidores.",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 42,
                                "nombre": "MARIA",
                                "apellido_1": "RODRIGUEZ",
                                "apellido_2": "LOPEZ",
                                "sexo": "FEMENINO",
                                "edad": 38,
                                "sueldo_bruto": 18500.00,
                                "sueldo_neto": 14820.50,
                                "sector": "Secretaría de Educación",
                                "puesto": "DOCENTE FRENTE A GRUPO",
                            }
                        ],
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
async def list_servidores(
    request: Request,
    filters: ServidorFilters = Depends(get_filters),
    session: AsyncSession = Depends(get_session),
):
    # Count query
    count_stmt = (
        select(func.count(P.id))
        .select_from(P)
        .join(N, N.persona_id == P.id)
    )
    count_stmt = apply_filters(count_stmt, filters)
    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    # Data query with JOINs for sector, puesto, and sexo names
    stmt = (
        select(
            P.id, P.nombre, P.apellido_1, P.apellido_2,
            CatSexo.nombre.label("sexo"), P.edad,
            N.sueldo_bruto, N.sueldo_neto,
            CatSector.nombre.label("sector"),
            CatPuesto.nombre.label("puesto"),
        )
        .select_from(P)
        .join(N, N.persona_id == P.id)
        .outerjoin(CatSexo, P.sexo_id == CatSexo.id)
        .outerjoin(CatSector, N.sector_id == CatSector.id)
        .outerjoin(CatPuesto, N.puesto_id == CatPuesto.id)
    )
    stmt = apply_filters(stmt, filters, _sexo_joined=True)
    stmt = apply_ordering(stmt, filters)
    stmt = stmt.offset((filters.page - 1) * filters.per_page).limit(filters.per_page)

    result = await session.execute(stmt)
    data = [
        ServidorListItem(
            id=r.id, nombre=r.nombre, apellido_1=r.apellido_1,
            apellido_2=r.apellido_2, sexo=r.sexo, edad=r.edad,
            sueldo_bruto=r.sueldo_bruto, sueldo_neto=r.sueldo_neto,
            sector=r.sector, puesto=r.puesto,
        )
        for r in result.all()
    ]

    return PaginatedResponse(
        data=data,
        total=total,
        page=filters.page,
        per_page=filters.per_page,
        pages=(total + filters.per_page - 1) // filters.per_page if total > 0 else 0,
    )


@router.get(
    "/stats",
    response_model=ServidorStats,
    summary="Estadísticas agregadas con filtros (panel reactivo)",
    description=(
        "Estadísticas sobre el subconjunto del padrón que matchea los "
        "filtros recibidos: total, promedio, mediana, percentiles "
        "(p25/p75), min/max de sueldo bruto, promedio de neto y edad, "
        "desglose por género con brecha %, y distribución por rangos de "
        "sueldo (`0-5K`, `5K-10K`, ..., `120K+`). Es el endpoint que "
        "alimenta el panel de filtros reactivo del laboratorio público. "
        "Cache HTTP `public, max-age=300`."
    ),
    responses={
        200: {
            "description": "Stats agregadas del subconjunto filtrado.",
            "content": {
                "application/json": {
                    "example": {
                        "total": 8230,
                        "sueldo_bruto_avg": 14820.50,
                        "sueldo_bruto_median": 12500.00,
                        "sueldo_bruto_p25": 9200.0,
                        "sueldo_bruto_p75": 18750.0,
                        "sueldo_bruto_min": 0.0,
                        "sueldo_bruto_max": 95000.0,
                        "sueldo_neto_avg": 12200.30,
                        "edad_avg": 38.5,
                        "count_hombres": 3100,
                        "count_mujeres": 5130,
                        "brecha_genero_pct": 12.4,
                        "distribucion_sueldo": [
                            {"rango": "5K-10K", "count": 1820},
                            {"rango": "10K-20K", "count": 4250},
                        ],
                    }
                }
            },
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (15 req/min por IP)."},
    },
)
@limiter.limit("15/minute")
async def servidor_stats(
    request: Request,
    filters: ServidorFilters = Depends(get_filters),
    session: AsyncSession = Depends(get_session),
):
    # Build WHERE clause from filters
    where_clauses = []
    params: dict = {}

    if filters.sector_id is not None:
        where_clauses.append("n.sector_id = :sector_id")
        params["sector_id"] = filters.sector_id
    if filters.sexo is not None:
        where_clauses.append("csex.nombre = :sexo")
        params["sexo"] = filters.sexo
    if filters.edad_min is not None:
        where_clauses.append("p.edad >= :edad_min")
        params["edad_min"] = filters.edad_min
    if filters.edad_max is not None:
        where_clauses.append("p.edad <= :edad_max")
        params["edad_max"] = filters.edad_max
    if filters.sueldo_min is not None:
        where_clauses.append("n.sueldo_bruto >= :sueldo_min")
        params["sueldo_min"] = filters.sueldo_min
    if filters.sueldo_max is not None:
        where_clauses.append("n.sueldo_bruto <= :sueldo_max")
        params["sueldo_max"] = filters.sueldo_max
    if filters.tipo_contratacion_id is not None:
        where_clauses.append("n.tipo_contratacion_id = :tipo_contratacion_id")
        params["tipo_contratacion_id"] = filters.tipo_contratacion_id
    if filters.tipo_personal_id is not None:
        where_clauses.append("n.tipo_personal_id = :tipo_personal_id")
        params["tipo_personal_id"] = filters.tipo_personal_id
    if filters.universo_id is not None:
        where_clauses.append("n.universo_id = :universo_id")
        params["universo_id"] = filters.universo_id
    if filters.puesto_search is not None:
        where_clauses.append("cp.nombre ILIKE :puesto_search")
        params["puesto_search"] = f"%{filters.puesto_search}%"

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
    join_puesto = "LEFT JOIN cdmx.cat_puestos cp ON n.puesto_id = cp.id" if filters.puesto_search else ""

    sql = f"""
    SELECT
        COUNT(*) AS total,
        AVG(n.sueldo_bruto)::float AS sueldo_bruto_avg,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY n.sueldo_bruto)::float AS sueldo_bruto_median,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY n.sueldo_bruto)::float AS sueldo_bruto_p25,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY n.sueldo_bruto)::float AS sueldo_bruto_p75,
        MIN(n.sueldo_bruto)::float AS sueldo_bruto_min,
        MAX(n.sueldo_bruto)::float AS sueldo_bruto_max,
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
    FROM cdmx.nombramientos n
    JOIN cdmx.personas p ON n.persona_id = p.id
    LEFT JOIN cdmx.cat_sexos csex ON p.sexo_id = csex.id
    {join_puesto}
    WHERE {where_sql}
    """

    result = await session.execute(text(sql), params)
    row = result.mappings().one()

    # Distribution query
    dist_sql = f"""
    SELECT
        CASE
            WHEN n.sueldo_bruto < 5000 THEN '0-5K'
            WHEN n.sueldo_bruto < 10000 THEN '5K-10K'
            WHEN n.sueldo_bruto < 20000 THEN '10K-20K'
            WHEN n.sueldo_bruto < 30000 THEN '20K-30K'
            WHEN n.sueldo_bruto < 50000 THEN '30K-50K'
            WHEN n.sueldo_bruto < 80000 THEN '50K-80K'
            WHEN n.sueldo_bruto < 120000 THEN '80K-120K'
            ELSE '120K+'
        END AS rango,
        COUNT(*) AS count
    FROM cdmx.nombramientos n
    JOIN cdmx.personas p ON n.persona_id = p.id
    LEFT JOIN cdmx.cat_sexos csex ON p.sexo_id = csex.id
    {join_puesto}
    WHERE {where_sql} AND n.sueldo_bruto IS NOT NULL
    GROUP BY rango
    ORDER BY MIN(n.sueldo_bruto)
    """
    dist_result = await session.execute(text(dist_sql), params)
    distribucion = [SueldoDistribucion(rango=r["rango"], count=r["count"]) for r in dist_result.mappings().all()]

    return ServidorStats(
        total=row["total"],
        sueldo_bruto_avg=row["sueldo_bruto_avg"],
        sueldo_bruto_median=row["sueldo_bruto_median"],
        sueldo_bruto_p25=row["sueldo_bruto_p25"],
        sueldo_bruto_p75=row["sueldo_bruto_p75"],
        sueldo_bruto_min=row["sueldo_bruto_min"],
        sueldo_bruto_max=row["sueldo_bruto_max"],
        sueldo_neto_avg=row["sueldo_neto_avg"],
        edad_avg=row["edad_avg"],
        count_hombres=row["count_hombres"],
        count_mujeres=row["count_mujeres"],
        brecha_genero_pct=row["brecha_genero_pct"],
        distribucion_sueldo=distribucion,
    )


@router.get(
    "/{servidor_id}",
    response_model=ServidorDetail,
    summary="Detalle de un servidor por ID",
    description=(
        "Detalle completo de un servidor (persona) por su ID numérico: "
        "datos personales, sueldo bruto/neto, fecha de ingreso, nivel "
        "salarial, sector, puesto, tipos de contratación/personal/nómina "
        "y universo. Cache HTTP `public, max-age=300`."
    ),
    responses={
        200: {"description": "Detalle del servidor."},
        404: {
            "model": HTTPError404,
            "description": "`servidor_id` no existe en `cdmx.personas`.",
            "content": {"application/json": {"example": {"detail": "Servidor no encontrado"}}},
        },
        429: {"model": HTTPError429, "description": "Rate limit excedido (60 req/min por IP)."},
    },
)
@limiter.limit("60/minute")
async def get_servidor(
    request: Request,
    servidor_id: int,
    session: AsyncSession = Depends(get_session),
):
    stmt = (
        select(
            P.id, P.nombre, P.apellido_1, P.apellido_2,
            CatSexo.nombre.label("sexo"), P.edad,
            N.sueldo_bruto, N.sueldo_neto,
            CatNivelSalarial.clave.label("id_nivel_salarial"),
            CatSector.nombre.label("sector"),
            CatPuesto.nombre.label("puesto"),
            CatTipoContratacion.nombre.label("tipo_contratacion"),
            CatTipoPersonal.nombre.label("tipo_personal"),
            cast(CatTipoNomina.clave, String).label("tipo_nomina"),
            CatUniverso.nombre.label("universo"),
        )
        .select_from(P)
        .join(N, N.persona_id == P.id)
        .outerjoin(CatSexo, P.sexo_id == CatSexo.id)
        .outerjoin(CatSector, N.sector_id == CatSector.id)
        .outerjoin(CatPuesto, N.puesto_id == CatPuesto.id)
        .outerjoin(CatTipoContratacion, N.tipo_contratacion_id == CatTipoContratacion.id)
        .outerjoin(CatTipoPersonal, N.tipo_personal_id == CatTipoPersonal.id)
        .outerjoin(CatTipoNomina, N.tipo_nomina_id == CatTipoNomina.id)
        .outerjoin(CatUniverso, N.universo_id == CatUniverso.id)
        .outerjoin(CatNivelSalarial, N.nivel_salarial_id == CatNivelSalarial.id)
        .where(P.id == servidor_id)
    )
    result = await session.execute(stmt)
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")

    return ServidorDetail(
        id=row.id, nombre=row.nombre, apellido_1=row.apellido_1,
        apellido_2=row.apellido_2, sexo=row.sexo, edad=row.edad,
        sueldo_bruto=row.sueldo_bruto, sueldo_neto=row.sueldo_neto,
        id_nivel_salarial=row.id_nivel_salarial,
        sector=row.sector, puesto=row.puesto,
        tipo_contratacion=row.tipo_contratacion, tipo_personal=row.tipo_personal,
        tipo_nomina=row.tipo_nomina, universo=row.universo,
    )
