# Proyecto final — Bases de Datos COM-12101-001

## ITAM, Primavera 2026

> Snapshot académico del Observatorio Datos México.

---

## Resumen del proyecto

Este repositorio es la entrega académica oficial del proyecto final
de la materia Bases de Datos COM-12101-001 del ITAM, semestre
Primavera 2026. Cubre las cinco etapas de la rúbrica del curso
(selección de dataset, limpieza y carga preliminar, normalización
hasta 4NF, análisis de resultados, y APIs REST con FastAPI) sobre
el **Padrón de Servidores Públicos de la Ciudad de México** (246,821
nombramientos vigentes al corte del dataset publicado en el Portal
de Datos Abiertos del Gobierno de la CDMX).

El trabajo dio origen al **Observatorio Datos México**, una iniciativa
de investigación con respaldo institucional del ITAM que hoy publica
cuatro datasets mexicanos vía SDK Python (PyPI), API REST pública y
sitio canónico institucional. Este repo recupera y documenta
fielmente el proceso académico inicial sobre el dataset CDMX que
detonó el observatorio.

---

## Equipo académico

Equipo técnico fundador del Observatorio Datos México. Información
extraída de `lib/team.ts` del repositorio del sitio canónico
(`Datos-Mexico/datos-mexico-site`, rama `main`), filtrando por
`tag === "equipo-tecnico-fundador"`.

| Nombre | Afiliación | GitHub |
|---|---|---|
| David Fernando Ávila Díaz | Estudiante de Ciencia de Datos, ITAM | [@DabtcAvila](https://github.com/DabtcAvila) |
| Gerardo André Butrón Ramírez | Estudiante de Ciencia de Datos, ITAM | [@butronand-png](https://github.com/butronand-png) |
| Emiliano Sebastián Millán Giffard | Estudiante de Ciencia de Datos, ITAM | [@emilianomillan](https://github.com/emilianomillan) |
| José Roberto Uribe Clemente | Estudiante de Ciencia de Datos, ITAM | [@RobertoUribeClemente](https://github.com/RobertoUribeClemente) |

El Observatorio Datos México, derivado del trabajo de este proyecto,
tiene actualmente una composición más amplia que incluye también
miembros incorporados después del cierre del entregable académico del
semestre. La composición vigente del observatorio se documenta en
[datosmexico.org/quienes-somos](https://datosmexico.org/quienes-somos).
Este repositorio refleja exclusivamente el equipo técnico fundador
que ejecutó el proyecto académico del curso COM-12101-001.

---

## Conjunto de datos

**Padrón de Servidores Públicos de la Ciudad de México**, dataset
abierto publicado por el Gobierno de la Ciudad de México en el
Portal de Datos Abiertos.

Cobertura empírica al corte preservado en el dump físico del
2026-04-20:

| Métrica | Valor |
|---|---|
| Total de nombramientos (filas) | 246,821 |
| Combinaciones identitarias únicas `(nombre, ap1, ap2, edad)` | 246,490 sobre 246,821 (99.87%) |
| Primeros nombres distintos (universo léxico) | 51,710 |
| Distintos apellidos paternos | 7,864 |
| Distintos apellidos maternos | 7,872 |
| Sectores de gobierno | 73 |
| Puestos distintos | 1,772 |
| Tipos de contratación | 7 |
| Tipos de personal | 11 |
| Tipos de nómina | 7 |
| Universos laborales | 27 |
| Niveles salariales | 721 |
| Sueldo bruto promedio | $13,225.32 MXN |
| Sueldo bruto mediana | $10,410.00 MXN |
| Edad promedio | 42.48 años |

La respuesta extensa a las 13 preguntas de la Etapa 1 de la rúbrica
(resumen, origen y autoría, justificación, disponibilidad y acceso,
periodicidad, dimensiones, diccionario, variables cuantitativas,
variables cualitativas, texto no estructurado, series temporales,
visión estratégica, consideraciones éticas) está en
[`docs/01-seleccion-dataset.md`](docs/01-seleccion-dataset.md).

---

## Etapas del proyecto

| # | Etapa | Documento académico | Artefactos versionados |
|---|---|---|---|
| 1 | Selección del conjunto de datos | [`docs/01-seleccion-dataset.md`](docs/01-seleccion-dataset.md) | — |
| 2 | Limpieza y carga preliminar | [`docs/02-limpieza-carga-preliminar.md`](docs/02-limpieza-carga-preliminar.md) | `sql/01-staging/*`, `sql/02-exploracion/*`, outputs en `evidencias/consultas-resultados/02-exploracion/` |
| 3 | Normalización hasta 4NF | [`docs/03-normalizacion-4nf.md`](docs/03-normalizacion-4nf.md) | `sql/03-normalizado/*`, `sql/04-migracion/*`, diagrama ER en [`docs/diagrama-entidad-relacion.md`](docs/diagrama-entidad-relacion.md) y `evidencias/diagrama-er.svg` |
| 4 | Análisis de resultados | [`docs/04-analisis-resultados.md`](docs/04-analisis-resultados.md) | `sql/05-analisis/*`, outputs en `evidencias/consultas-resultados/05-analisis/` |
| 5 | APIs REST con FastAPI | [`docs/05-api-fastapi.md`](docs/05-api-fastapi.md) | `api/app/*`, `api/migrations/*`, `api/tests/*` |

Documentos académicos complementarios:

- [`docs/diccionario-datos.md`](docs/diccionario-datos.md) — diccionario por columna del esquema 4NF.
- [`docs/dependencias-funcionales.md`](docs/dependencias-funcionales.md) — DFs no triviales y dependencias multivaluadas detectadas en el proceso de normalización.
- [`docs/consideraciones-eticas.md`](docs/consideraciones-eticas.md) — sesgos, datos sensibles, dilemas y mitigaciones aplicadas.
- [`docs/relacion-con-observatorio.md`](docs/relacion-con-observatorio.md) — narrativa académica del salto desde el proyecto del curso al Observatorio Datos México.

---

## Relación con el Observatorio Datos México

Este repositorio es la entrega académica del proyecto del semestre.
El mismo trabajo, una vez completado, dio origen al
**Observatorio Datos México**, una iniciativa de investigación con
respaldo institucional del ITAM que hoy publica cuatro datasets
mexicanos (CDMX servidores públicos + ENIGH 2024 + CONSAR AFORE
recursos + ENOE 15+) vía:

- **SDK Python** [`datos-mexico`](https://pypi.org/project/datos-mexico/) instalable con `pip install datos-mexico`.
- **API REST pública** en [`api.datos-itam.org`](https://api.datos-itam.org) con OpenAPI documentado.
- **Sitio canónico** institucional en [`datosmexico.org`](https://datosmexico.org).

Este repo académico se limita intencionalmente al **dataset CDMX**
para mantener el scope del proyecto del curso. La expansión a los
otros tres datasets ocurrió después del cierre del entregable
académico y se documenta en
[`docs/relacion-con-observatorio.md`](docs/relacion-con-observatorio.md).

---

## Open source y disponibilidad pública del observatorio

El Observatorio Datos México publica como open source los componentes
consumibles por terceros:

- **SDK Python `datos-mexico`** — código fuente público en
  [`github.com/Datos-Mexico/datos-mexico-py`](https://github.com/Datos-Mexico/datos-mexico-py),
  paquete disponible en PyPI (`pip install datos-mexico`),
  licencia MIT.
- **Sitio canónico `datosmexico.org`** — código fuente público en
  [`github.com/Datos-Mexico/datos-mexico-site`](https://github.com/Datos-Mexico/datos-mexico-site),
  licencia MIT.
- **API REST pública** — `api.datos-itam.org` sirve los endpoints
  analíticos sin autenticación; especificación OpenAPI disponible
  en `api.datos-itam.org/openapi.json`.
- **Este repo académico** — snapshot del backend para el dataset
  CDMX, scripts SQL ejecutables del proceso académico, documentación
  completa, licencia MIT.

El código del backend de producción completo (con los endpoints de
los otros tres datasets del observatorio: ENIGH, CONSAR, ENOE)
permanece en repositorio privado mientras se mitiga una deuda
técnica registrada (credencial de base de datos histórica presente
en historia git). El observatorio reconoce públicamente esta deuda
y trabaja hacia hacer pública la totalidad del código del backend
como roadmap futuro.

**Disponibilidad pragmática hoy**:

- Cualquier investigador externo puede consumir los datos del
  observatorio vía SDK Python o API REST sin restricción.
- Cualquier persona puede leer y reproducir el proceso académico
  documentado en este repo.
- Cualquier persona puede leer el código del SDK y del sitio canónico.

---

## Cómo replicar este proyecto

### Requisitos

- PostgreSQL ≥ 16 local
- Python ≥ 3.13
- [`uv`](https://github.com/astral-sh/uv) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Acceso al CSV original del Padrón CDMX (Portal de Datos Abiertos
  del Gobierno de la CDMX) **o** al dump físico
  `remuneraciones_cdmx.dump` (4.8 MB, formato PostgreSQL custom)
  preservado por el equipo técnico fundador.

### Paso 1 — Crear base de datos local

```bash
createdb proyecto_academico
```

### Paso 2A — Cargar staging desde el dump físico (fidelidad máxima)

```bash
pg_restore -d proyecto_academico --no-owner --no-privileges \
  /path/to/remuneraciones_cdmx.dump
```

### Paso 2B — Alternativa: cargar staging desde el CSV original

```bash
psql -d proyecto_academico -f sql/01-staging/01-create-staging.sql
psql -d proyecto_academico -c "\copy servidores_publicos FROM 'padron-cdmx.csv' CSV HEADER"
# (Ver sql/01-staging/02-cargar-csv.sql para la versión completa con catálogos.)
```

### Paso 3 — Ejecutar exploración SQL (Etapa 2)

```bash
for f in sql/02-exploracion/*.sql; do
  echo "--- $f ---"
  psql -d proyecto_academico -f "$f"
done
```

### Paso 4 — Normalizar a 4NF (Etapa 3)

```bash
psql -d proyecto_academico -f sql/03-normalizado/01-create-tablas-normalizadas.sql
psql -d proyecto_academico -f sql/04-migracion/01-staging-a-normalizado.sql
psql -d proyecto_academico -f sql/03-normalizado/02-create-indexes.sql
```

### Paso 5 — Análisis avanzado (Etapa 4)

```bash
for f in sql/05-analisis/*.sql; do
  echo "--- $f ---"
  psql -d proyecto_academico -f "$f"
done
```

### Paso 6 — Levantar la API REST (Etapa 5)

```bash
cd api/
cp .env.example .env
# Editar .env con la URL apropiada apuntando a proyecto_academico.
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Abrir Swagger UI
open http://localhost:8000/docs
```

> **Nota sobre migraciones del backend (`api/migrations/`)**: las
> migraciones SQL del paquete `api/migrations/` son la cadena que el
> backend completo del observatorio aplica sobre Neon. Si seguiste
> los pasos 4 y 5 de este README, la normalización ya está
> completa: en ese caso **omite `migrations/001_normalize.sql`** (la
> base ya está normalizada) y aplica únicamente
> `migrations/002_users.sql`, `003_indexes_and_extensions.sql`,
> `004_materialized_views.sql`, `005_multischema_cdmx.sql`, y
> `008_users_is_admin.sql`. Si en cambio cargaste sólo el staging
> (paso 2A o 2B) sin normalizar, aplica también `001_normalize.sql`.

### Paso 7 — Correr la suite de tests (opcional)

```bash
cd api/
TESTING=1 uv run pytest -v
```

---

## Disciplina académica

Ver [`docs/disciplina-academica.md`](docs/disciplina-academica.md) para
las políticas de commits, autoría, y la documentación de la excepción
de bootstrap del repositorio.

---

## Licencia

[MIT](LICENSE) © 2026 David Fernando Ávila Díaz.
