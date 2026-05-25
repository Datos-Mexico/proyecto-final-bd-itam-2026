# Plan de aplicación de correcciones del peer review académico externo

Documento interno del equipo técnico fundador. Registra la matriz
completa de cambios que se aplicarán sobre el repositorio académico
en respuesta al peer review externo independiente ejecutado el
2026-05-25, antes de hacer público el repo + invitar al profesor.

Branch de trabajo: `fix/peer-review-corrections`. Ningún cambio toca
`main` directamente; cada sub-fase termina con commits granulares y
el PR formal se abre al final.

---

## 1. Lectura empírica honesta (fuente única de verdad)

Toda corrección académica de cifras y narrativa se ancla en esta
tabla. Los valores provienen de outputs versionados en
`evidencias/consultas-resultados/`, **no de estimaciones**.

| Métrica | Valor empírico | Fuente |
|---|---|---|
| Total nombramientos (filas) | 246,821 | `evidencias/consultas-resultados/02-exploracion/01-valores-unicos.txt` |
| Cuartetos `(nombre, ap1, ap2, edad)` únicos | 246,490 | `evidencias/consultas-resultados/02-exploracion/04-duplicados-categoricos.txt` |
| Cuartetos que se repiten | 305 | mismo archivo |
| Filas con cuarteto duplicado | 636 (0.26%) | mismo archivo |
| Nombres de pila distintos (universo léxico) | 51,710 | `01-valores-unicos.txt` |
| Apellidos paternos distintos (universo léxico) | 7,864 | `01-valores-unicos.txt` |
| Apellidos maternos distintos (universo léxico) | 7,872 | `01-valores-unicos.txt` |

Lectura honesta: el padrón tiene esencialmente una persona única por
nombramiento (99.87% de cuartetos únicos). La duplicación cuarteto
es marginal (0.26%) y probablemente representa homónimos genuinos.
Sin acceso a CURP/RFC no es posible deduplicar personas físicas con
certeza académica.

---

## 2. Reformulación académica del motor empírico de 4NF

El motor empírico previo de la decisión 4NF (la deduplicación
implícita de personas físicas) se sobre-interpretaba. La
justificación académicamente honesta para la normalización a 4NF se
reformula como:

1. Separar entidades léxicas de tabuladores administrativos.
2. Estructura relacional limpia para análisis dimensional.
3. Reducir redundancia textual (51,710 nombres en catálogo
   reutilizable + 246,821 referencias FK vs 246,821 strings
   repetidos).
4. Catalogación de tabuladores salariales (721 niveles, hoy sueltos
   como `INTEGER` sin tabla referida).
5. Preparación estructural para integración futura si se obtiene un
   identificador único (CURP, RFC) que permita deduplicar.

La separación `personas` / `nombramientos` se preserva como decisión
4NF correcta, pero ya no apoyada en duplicación masiva que no se
observa empíricamente.

---

## 3. Matriz de cambios

Cada fila incluye: hallazgo, severidad, archivo, líneas afectadas,
texto actual, texto propuesto, commit.

### 3.1 — BLOQUEANTE

#### B1 · README.md

- **Archivo**: `README.md`
- **Severidad**: BLOQUEANTE
- **Líneas afectadas**: 16-18 (texto-titular), 57 (fila de tabla),
  71 (referencia a "16 preguntas")
- **Líneas 16-18 — texto actual**:

  > "el **Padrón de Servidores Públicos de la Ciudad de México** (246,821
  > nombramientos vigentes al corte del dataset publicado en el Portal
  > de Datos Abiertos del Gobierno de la CDMX)."

  Esta línea es correcta; no se modifica. La mischaracterización en
  el README maestro ocurre en la sub-tabla "Cobertura empírica".

- **Línea 57 — texto actual**:

  ```markdown
  | Distintos nombres de pila | 51,710 |
  ```

- **Línea 57 — texto propuesto** (reemplazar la fila por dos filas
  que distingan identidad léxica de identidad personal):

  ```markdown
  | Combinaciones identitarias únicas `(nombre, ap1, ap2, edad)` | 246,490 sobre 246,821 (99.87%) |
  | Primeros nombres distintos (universo léxico) | 51,710 |
  ```

- **Commit**: `fix(README): corregir mischaracterización de 51,710 como personas físicas (B1)`

#### B1 (eco) · docs/01-seleccion-dataset.md

- **Archivo**: `docs/01-seleccion-dataset.md`
- **Severidad**: BLOQUEANTE
- **Líneas afectadas**: 17-21 (sección 1. Resumen), 91 (fila del
  diccionario sintético)
- **Líneas 17-21 — texto actual**:

  > "Al corte preservado en el dump físico del 2026-04-20, el dataset
  > registra **246,821 nombramientos** distribuidos en **73 sectores de
  > gobierno** con **51,710 identidades distintas** (personas físicas
  > con uno o más nombramientos vigentes)."

- **Líneas 17-21 — texto propuesto** (reformulación literal del
  prompt §3.4):

  > "Al corte preservado en el dump físico del 2026-04-20, el dataset
  > registra **246,821 nombramientos** distribuidos en **73 sectores de
  > gobierno** con **246,490 cuartetos identitarios únicos** sobre
  > `(nombre, apellido_1, apellido_2, edad)`. Sin acceso a un
  > identificador único como CURP o RFC, no es posible determinar con
  > certeza cuántas personas físicas distintas componen el padrón; los
  > 305 cuartetos que se repiten (en 636 filas, 0.26% del total) pueden
  > corresponder a homónimos genuinos o a la misma persona con
  > múltiples nombramientos."

- **Línea 91 — texto actual**:

  ```markdown
  | `nombre` | texto identitario | 51,710 distintos | Primer nombre del servidor. |
  ```

- **Línea 91 — texto propuesto** (aclarar que la cifra es del
  universo léxico):

  ```markdown
  | `nombre` | texto identitario | 51,710 strings distintos (universo léxico) | Primer nombre del servidor. |
  ```

- **Commit**: `fix(docs/01): alinear terminología empírica de cuartetos identitarios vs nombres léxicos (B1)`

### 3.2 — VALE AJUSTAR

#### V1 (H2) · docs/consideraciones-eticas.md §6

- **Archivo**: `docs/consideraciones-eticas.md`
- **Severidad**: VALE AJUSTAR
- **Líneas afectadas**: 115-136 (sección 6 completa)
- **Líneas 117-124 — texto actual**:

  > "El esquema 4NF separa `personas` de `nombramientos`, pero la
  > migración inicial **no deduplica** personas con múltiples
  > nombramientos (mapeo 1:1 entre filas del CSV y filas de
  > `personas`). Esto deja un **artefacto académico**: el conteo
  > `SELECT COUNT(*) FROM personas` (246,821) es igual al conteo de
  > nombramientos, pero la realidad social es que hay
  > probablemente ~150,000 personas físicas que ocupan esos 246,821
  > nombramientos."

- **Líneas 117-124 — texto propuesto** (reformulación literal del
  prompt §3.4):

  > "El conteo `SELECT COUNT(*) FROM personas` arroja 246,821, igual al
  > conteo de nombramientos. La evidencia empírica disponible (246,490
  > cuartetos identitarios únicos sobre `(nombre, apellido_1,
  > apellido_2, edad)`) sugiere que el padrón tiene esencialmente una
  > persona única por nombramiento, con solamente 305 cuartetos
  > repetidos en 636 filas (0.26%). Sin acceso a un identificador único
  > como CURP o RFC, no es posible deduplicar personas físicas con
  > certeza académica: los cuartetos repetidos podrían corresponder a
  > homónimos genuinos (personas distintas con el mismo nombre,
  > apellidos y edad) o a la misma persona con múltiples nombramientos.
  > La normalización a 4NF aplicada en este proyecto NO pretende
  > deduplicar personas físicas; separa entidades léxicas (nombres,
  > apellidos) en catálogos reutilizables y normaliza los tabuladores
  > administrativos, dejando el padrón estructuralmente listo para una
  > futura deduplicación si se obtiene acceso a un identificador
  > único."

  Las líneas 126-136 (caveat académico de tres puntos + cierre) se
  preservan tal cual; el cambio toca únicamente el primer párrafo
  de §6.

- **Commit**: `fix(docs/etica): eliminar estimación inventada '~150K personas' y reformular sobre evidencia empírica real (V1)`

#### V2 (H3) · docs/02-limpieza-carga-preliminar.md

- **Archivo**: `docs/02-limpieza-carga-preliminar.md`
- **Severidad**: VALE AJUSTAR
- **Líneas afectadas**: 43-46 (sub-sección "Valores únicos"),
  71-79 (sub-sección "Duplicados categóricos"), 124-129 (conclusión
  para Etapa 3)
- **Líneas 44-45 — texto actual**:

  > "51,710 nombres distintos sobre 246,821 filas — fuerte indicio de
  > personas con múltiples nombramientos."

- **Líneas 44-45 — texto propuesto** (reformulación literal del
  prompt §3.4):

  > "51,710 strings distintos en `nombre` (universo léxico de primeros
  > nombres como `JUAN`, `MARÍA`), no del número de personas físicas:
  > la evidencia empírica sobre el cuarteto identitario `(nombre, ap1,
  > ap2, edad)` muestra 246,490 cuartetos únicos sobre 246,821 filas
  > (99.87%), indicando duplicación marginal."

- **Líneas 71-79 — texto actual**:

  > "El cuarteto identitario `(nombre, apellido_1, apellido_2, edad)`
  > aparece más de una vez en miles de casos. Este hallazgo es el
  > **motor empírico de la decisión de normalización a 4NF**: una
  > persona física puede ocupar varios nombramientos simultáneos o
  > consecutivos, por lo que separar identidad (`personas`) de relación
  > laboral (`nombramientos`) es la decisión 4NF correcta. Esta
  > separación elimina la dependencia funcional implícita
  > `{nombre, apellido_1, apellido_2, edad} → atributos identitarios`
  > que en la tabla desnormalizada se duplicaría en cada fila."

- **Líneas 71-79 — texto propuesto** (reformulación literal del
  prompt §3.4 + ajuste del motor empírico §3.3):

  > "El cuarteto identitario `(nombre, apellido_1, apellido_2, edad)`
  > aparece más de una vez en 305 casos (636 filas, 0.26% del padrón).
  > La duplicación cuarteto es marginal y probablemente representa
  > homónimos genuinos (personas distintas con mismo nombre, apellidos
  > y edad). Sin acceso a CURP/RFC no es posible determinar con
  > certeza si los 305 cuartetos repetidos corresponden a homónimos o
  > a la misma persona en múltiples nombramientos.
  >
  > La decisión académica de normalizar a 4NF separando `personas` y
  > `nombramientos` se justifica empíricamente NO por una duplicación
  > masiva que el padrón no exhibe, sino por:
  > (a) separar entidades léxicas (nombres, apellidos) de tabuladores
  > administrativos del nombramiento; (b) reducir redundancia textual
  > (51,710 strings en catálogo reutilizable + 246,821 referencias FK
  > vs 246,821 strings repetidos); (c) dejar el esquema
  > estructuralmente listo para una futura deduplicación de personas
  > si se obtiene acceso a un identificador único."

- **Líneas 124-129 — texto actual** (conclusión 2 para Etapa 3):

  > "**Separación `personas` / `nombramientos`** — el hallazgo de
  > cuartetos identitarios repetidos confirma que el padrón
  > contiene `1 fila por nombramiento`, no `1 fila por persona`.
  > Para preservar la dependencia funcional `persona_id → {nombre,
  > apellido_1, apellido_2, sexo, edad}` y eliminar la dependencia
  > multivaluada implícita, se requiere split en dos tablas."

- **Líneas 124-129 — texto propuesto** (alinear el motor empírico
  con la realidad medida):

  > "**Separación `personas` / `nombramientos`** — el padrón publica
  > una fila por nombramiento vigente, no una fila por persona. Aunque
  > empíricamente la duplicación cuarteto es marginal (0.26%), el
  > split académicamente correcto separa entidades léxicas (nombre,
  > apellidos, sexo, edad) de los atributos laborales del
  > nombramiento, reduce redundancia textual, y deja el esquema
  > preparado para integrar deduplicación futura si se obtiene un
  > identificador único como CURP o RFC."

- **Commit**: `fix(docs/02): suavizar retórica de duplicación con cifras empíricas precisas (V2)`

#### V2 (eco) · docs/03-normalizacion-4nf.md

- **Archivo**: `docs/03-normalizacion-4nf.md`
- **Severidad**: VALE AJUSTAR (encadenado con V2)
- **Líneas afectadas**: 6-11 (resumen ejecutivo), 49-52 (DMV
  persona → nombramientos), 106-111 (verificación empírica), 115-125
  (caveat 1 sobre deduplicación)
- **Justificación**: el doc Etapa 3 hereda el motor empírico
  reformulado en V2. Hay que actualizar las cuatro secciones para
  mantener narrativa coherente.

- **Líneas 6-11 — texto actual**:

  > "Esta etapa transforma el estado raw de staging (tabla
  > `servidores_publicos` desnormalizada con seis catálogos extraídos)
  > al esquema final 4NF compuesto por **diez tablas**: `personas`,
  > `nombramientos`, y ocho catálogos. La transformación está
  > empíricamente justificada por los hallazgos de la Etapa 2 (cuartetos
  > identitarios repetidos, `sexo` y `nivel_salarial` con baja
  > cardinalidad)."

- **Líneas 6-11 — texto propuesto**:

  > "Esta etapa transforma el estado raw de staging (tabla
  > `servidores_publicos` desnormalizada con seis catálogos extraídos)
  > al esquema final 4NF compuesto por **diez tablas**: `personas`,
  > `nombramientos`, y ocho catálogos. La transformación está
  > empíricamente justificada por los hallazgos de la Etapa 2: `sexo`
  > y `nivel_salarial` con baja cardinalidad (catalogables), y
  > redundancia textual de cuartetos identitarios sobre 246,821 filas
  > que ameritan separación de entidades léxicas (nombre, apellidos) en
  > una tabla `personas` distinta de la relación laboral
  > (`nombramientos`)."

- **Líneas 49-52 — texto actual**:

  > "**Dependencia multivaluada**: `persona → nombramientos`. Una
  > persona puede tener N nombramientos. La normalización a 4NF
  > separa este 1:N en dos tablas (`personas` y `nombramientos` con
  > FK `persona_id`)."

- **Líneas 49-52 — texto propuesto**:

  > "**Dependencia multivaluada potencial**: `persona → nombramientos`.
  > El modelo permite que una persona física tenga N nombramientos. El
  > padrón vigente al corte exhibe duplicación marginal (305 cuartetos
  > en 636 filas, 0.26%), por lo que la cardinalidad observada es
  > esencialmente 1:1. La normalización a 4NF separa estructuralmente
  > en dos tablas (`personas` y `nombramientos` con FK `persona_id`)
  > para acomodar la dependencia multivaluada cuando se obtenga un
  > identificador único que permita deduplicar."

- **Líneas 106-111 — texto actual** (verificación empírica):

  > "La relación inicial 1:1 entre `personas` y `nombramientos` es
  > correcta porque el padrón publica una fila por nombramiento vigente;
  > si una persona física aparece en dos nombramientos, el split la
  > duplica en `personas` con dos `id` distintos (esto es una decisión
  > académica simplificadora — en un modelo de producción se requeriría
  > una clave natural para deduplicar; ver caveats abajo)."

- **Líneas 106-111 — texto propuesto**:

  > "La relación inicial 1:1 entre `personas` y `nombramientos` es
  > correcta porque el padrón publica una fila por nombramiento
  > vigente y la migración no aplica deduplicación. El esquema final
  > permite cardinalidad N:1 (varios nombramientos apuntando a la
  > misma persona) cuando se obtenga un identificador único; mientras
  > tanto, los 305 cuartetos identitarios que se repiten en 636 filas
  > (0.26%) producen registros separados en `personas` que podrían
  > consolidarse mediante record linkage futuro (ver caveats abajo)."

- **Líneas 115-125 — texto actual** (caveat 1):

  > "**Deduplicación de personas físicas**: la migración del CSV al
  > esquema normalizado **no deduplica** personas físicas con
  > múltiples nombramientos. Esto es porque el CSV no provee una
  > clave natural confiable (no hay CURP, RFC ni identificador
  > único) y la combinación `(nombre, apellido_1, apellido_2, edad)`
  > tiene falsos positivos (homónimos legítimos). En un sistema de
  > producción real se aplicaría record linkage probabilístico; en
  > este proyecto académico se opta por preservar 1:1 en la
  > migración inicial y exponer la dependencia multivaluada como
  > modelo formal (`nombramientos.persona_id` permite N→1 si futura
  > deduplicación lo amerita)."

- **Líneas 115-125 — texto propuesto**:

  > "**Deduplicación de personas físicas**: la migración del CSV al
  > esquema normalizado **no deduplica** personas físicas. La
  > evidencia empírica (246,490 cuartetos únicos sobre 246,821 filas,
  > 99.87%) sugiere que la deduplicación realista colapsaría como
  > máximo 331 filas, no un porcentaje material del padrón. Sin un
  > identificador único en el CSV (CURP, RFC) no se puede distinguir
  > entre los 305 cuartetos duplicados que son homónimos genuinos vs
  > la misma persona en múltiples nombramientos. En este proyecto
  > académico se preserva el mapeo 1:1 en la migración inicial y se
  > expone la dependencia multivaluada como modelo formal:
  > `nombramientos.persona_id` permite N→1 si el padrón futuro
  > incorpora un identificador único que habilite record linkage."

- **Commit**: `fix(docs/03): reformular justificación académica de 4NF sobre motor empírico honesto`

### 3.3 — VALE AJUSTAR (técnico/documentario)

#### V3 · README.md (conteo de preguntas Etapa 1)

- **Archivo**: `README.md`
- **Severidad**: VALE AJUSTAR
- **Líneas afectadas**: 71-76
- **Decisión empírica**: la rúbrica oficial del curso enumera **13
  preguntas** en la sección "Archivo README.md" de la Etapa 1
  (Resumen, Origen y Autoría, Justificación, Disponibilidad y
  Acceso, Periodicidad de Actualización, Dimensiones, Diccionario
  de Datos, Variables Cuantitativas, Variables Cualitativas, Texto
  No Estructurado, Series Temporales, Visión Estratégica,
  Consideraciones Éticas). Son 13, no 16. El doc Etapa 1 ya tiene
  13 secciones — el error está en el README.
- **Línea 71 — texto actual**:

  > "La respuesta extensa a las 16 preguntas de la Etapa 1 de la rúbrica"

- **Línea 71 — texto propuesto**:

  > "La respuesta extensa a las 13 preguntas de la Etapa 1 de la rúbrica"

- **Commit**: `fix(docs/01): reconciliar conteo de preguntas Etapa 1 contra rúbrica oficial (V3)`

#### V4 · api/README.md (línea fantasma alembic-style)

- **Archivo**: `api/README.md`
- **Severidad**: VALE AJUSTAR
- **Línea afectada**: 83
- **Texto actual** (línea 83):

  ```
  uv run alembic-style apply           # (Ver migrations/ — aplicar SQL plano)
  ```

- **Acción**: eliminar la línea (más la siguiente línea en blanco si
  queda gap visible). Justo después de `uv sync` queda directamente
  el comentario `# Aplicar migraciones manualmente sobre la base
  local:` seguido de los `psql ...` reales.
- **Commit**: `fix(api/README): eliminar línea fantasma uv run alembic-style apply (V4)`

#### V5 · api/main.py (stub Hello)

- **Archivo**: `api/main.py`
- **Severidad**: VALE AJUSTAR
- **Líneas afectadas**: archivo completo (7 líneas)
- **Decisión**: el archivo es entry point por defecto que `uv init`
  genera al crear el paquete. Como el README maestro y el doc de
  Etapa 5 documentan la API en `app.main:app` (corrida con
  `uv run uvicorn app.main:app`), `api/main.py` no aporta valor. Se
  reemplaza por un mensaje informativo que apunta al entry point
  real (alternativa más conservadora que eliminar el archivo, que
  podría romper expectativas de `python -m api`).
- **Texto actual**:

  ```python
  def main():
      print("Hello from api!")


  if __name__ == "__main__":
      main()
  ```

- **Texto propuesto**:

  ```python
  """Entry point informativo del paquete `api`.

  La aplicación FastAPI real vive en `app.main:app`. Para arrancar
  el servidor en local:

      uv run uvicorn app.main:app --reload --port 8000

  Este módulo se conserva como referencia mínima y emite un mensaje
  guía cuando se ejecuta directamente.
  """


  def main() -> None:
      print(
          "Para arrancar la API ejecuta:\n"
          "    uv run uvicorn app.main:app --reload --port 8000"
      )


  if __name__ == "__main__":
      main()
  ```

- **Commit**: `fix(api): reemplazar stub api/main.py por entry point real (V5)`
- **Eco en docs/05-api-fastapi.md líneas 13-14**: el bullet
  `1 entry point (api/main.py)` se actualiza a
  `1 entry point informativo (api/main.py — apunta al servidor real en app.main:app)`
  para mantener coherencia con el cambio.

#### V6 · api/migrations/005_multischema_cdmx.sql (comentario search_path obsoleto)

- **Archivo**: `api/migrations/005_multischema_cdmx.sql`
- **Severidad**: VALE AJUSTAR
- **Líneas afectadas**: 15-17
- **Texto actual**:

  ```
  -- The app uses unqualified table names everywhere; setting
  -- `search_path='cdmx, public'` in app/database.py lets existing SQL resolve
  -- to cdmx.* first and falls back to public.* for `users`.
  ```

- **Texto propuesto** (reflejar realidad post-pgbouncer, alineada
  con el comentario que ya existe en `app/database.py`):

  ```
  -- The app resolves namespaces via explicit schema qualification:
  -- SQLModel models declare `__table_args__ = {"schema": "cdmx"}` and
  -- raw SQL strings prefix tables with `cdmx.*` (CDMX) or `public.*`
  -- (users). A connection-level `search_path` is NOT used because
  -- Neon's pgbouncer transaction pooling does not preserve session
  -- state across transactions — a startup-time search_path would
  -- drop out whenever pgbouncer hands a query to a different backend.
  ```

- **Commit**: `fix(migrations/005): actualizar comentario sobre search_path post-pgbouncer (V6)`

### 3.4 — OBSERVACIÓN MENOR (excepto O7)

#### O1 · Referencias a endpoints fuera del snapshot

- **Archivos**:
  - `api/migrations/004_materialized_views.sql` líneas 6-7
  - `docs/diagrama-entidad-relacion.md` línea 125
- **Texto actual en 004 (línea 6-7)**:

  ```
  -- Refresh strategy: POST /api/v1/admin/refresh-materialized-views
  -- (JWT-protected). Call after /api/v1/ingest/csv runs or on a nightly cron.
  ```

- **Texto propuesto en 004**:

  ```
  -- Refresh strategy en producción: POST /api/v1/admin/refresh-materialized-views
  -- (JWT-protected, presente sólo en el backend completo del observatorio,
  -- NO en este snapshot académico). En local se refresca corriendo
  -- `REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dashboard_<name>;` directamente
  -- vía psql después de re-poblar los datos.
  ```

- **Texto actual en diagrama-entidad-relacion.md (línea 125)**:

  > "Refresh: `POST /api/v1/admin/refresh-materialized-views`
  > (JWT-protected), corre `REFRESH MATERIALIZED VIEW CONCURRENTLY`
  > sobre los 5."

- **Texto propuesto**:

  > "Refresh en producción: `POST /api/v1/admin/refresh-materialized-views`
  > (JWT-protected, expuesto sólo en el backend completo del
  > observatorio, no en este snapshot académico). En local se refrescan
  > manualmente vía psql con `REFRESH MATERIALIZED VIEW CONCURRENTLY
  > cdmx.mv_dashboard_<name>;` sobre las 5."

- **Commit**: `fix(migrations,docs/er): aclarar referencias a endpoints fuera del snapshot (O1)`

#### O2 · docs/relacion-con-observatorio.md (referencia a audit interno)

- **Archivo**: `docs/relacion-con-observatorio.md`
- **Línea afectada**: 23
- **Texto actual**:

  > "| **2026-05-23** | Audit interno completo del observatorio (Fase 1
  > inventario + Fase 2 contrato API). Reportes en
  > `docs/internal/audit-2026-05/`. |"

- **Texto propuesto** (aclarar que es del repo privado, no de este
  repo):

  > "| **2026-05-23** | Audit interno completo del observatorio (Fase 1
  > inventario + Fase 2 contrato API). Reportes preservados en
  > `docs/internal/audit-2026-05/` del repositorio privado del
  > backend del observatorio — no están en este repo académico. |"

- **Commit**: `fix(docs/observatorio): aclarar que docs/internal/audit-2026-05/ es del repo privado (O2)`

#### O3 · sql/05-analisis/04-percentiles-por-grupo.sql

- **Archivo**: `sql/05-analisis/04-percentiles-por-grupo.sql`
- **Línea afectada**: 15
- **Texto actual**:

  ```sql
  WHEN p.edad < 26 THEN '1. 18-25'
  ```

- **Decisión**: el rango etario empírico mínimo del padrón es 16
  años (no 18). El bucket `'1. 18-25'` incluía silenciosamente
  ages 16-17. Se renombra el label a `'1. 16-25'` para reflejar
  el rango real.
- **Texto propuesto**:

  ```sql
  WHEN p.edad < 26 THEN '1. 16-25'
  ```

- **Eco en docs**:
  - `docs/04-analisis-resultados.md` línea con "$15,275 para
    hombres 18-25" → ajustar a "16-25".
- **Commit**: `fix(sql/05,docs/04): corregir label de bucket etario para incluir 16-17 (O3)`

#### O4 · api/app/main.py (datos.gob.mx → datos.cdmx.gob.mx)

- **Archivo**: `api/app/main.py`
- **Línea afectada**: 27
- **Texto actual**:

  > "- **Servidores públicos CDMX** (schema `cdmx`): 246K registros del Padrón
  >   de Servidores Públicos de la Ciudad de México (datos.gob.mx)."

- **Texto propuesto**:

  > "- **Servidores públicos CDMX** (schema `cdmx`): 246K registros del Padrón
  >   de Servidores Públicos de la Ciudad de México (datos.cdmx.gob.mx)."

- **Commit**: `fix(api/main): corregir referencia datos.gob.mx → datos.cdmx.gob.mx (O4)`

#### O5 · api/app/auth.py y api/pyproject.toml

- **Archivos**:
  - `api/app/auth.py` líneas 67-74 (`require_demo_user` huérfano)
  - `api/pyproject.toml` línea 17 (`dbfread`)

- **`require_demo_user`**: helper para endpoints `/demo/*` que el
  snapshot académico NO expone (documentado explícitamente en
  `api/README.md` "Diferencias con el backend de producción"). Se
  elimina el helper para que el código del snapshot no contenga
  dependencias huérfanas.

- **`dbfread`**: lector de archivos DBF usado en producción para
  ENIGH/CONSAR. Ningún módulo del snapshot CDMX la importa. Se
  elimina de `pyproject.toml`.

- **Texto actual (auth.py 67-74)**:

  ```python
  async def require_demo_user(current_user: User = Depends(get_current_user)) -> User:
      """Cualquier usuario autenticado (admin o no) puede operar el toggle de /demo.

      Alias semántico de get_current_user para que la firma del endpoint declare
      explícitamente "esto requiere login pero no privilegios admin". Útil para
      diferenciarlo visualmente de require_admin en /admin/demo/*.
      """
      return current_user
  ```

- **Acción**: eliminar el bloque completo + la línea en blanco
  previa.

- **Texto actual (pyproject.toml línea 17)**:

  ```toml
      "dbfread>=2.0.7",
  ```

- **Acción**: eliminar la línea.

- **Commit**: `fix(api): limpiar require_demo_user huérfano y dependencia dbfread no usada (O5)`

#### O6 · docs/diagrama-entidad-relacion.md (cosmético)

- **Archivo**: `docs/diagrama-entidad-relacion.md`
- **Líneas afectadas**: 221 (cat_tipos_personal aprox.), 226-230
  (regenerate-erd placeholder), 207 (DBML — `users` table sin
  is_admin field para coherencia con 008_users_is_admin.sql)

- **Línea 221 — texto actual**:

  ```markdown
  | `cat_tipos_personal` | 11 (aprox.) |
  ```

- **Línea 221 — texto propuesto**:

  ```markdown
  | `cat_tipos_personal` | 11 |
  ```

- **Líneas 226-230 — texto actual** (placeholder de script
  inexistente):

  ```markdown
  Regenera este doc cuando cambie el schema:
  ```bash
  # (cuando tengamos un script de generación)
  ./api/scripts/regenerate-erd
  ```
  ```

- **Líneas 226-230 — texto propuesto** (sustituir por instrucción
  manual real):

  ```markdown
  Cuando cambie el schema, regenera manualmente el diagrama
  ejecutando `pg_dump --schema-only` sobre la base local y
  actualizando el bloque Mermaid + DBML de este documento.
  ```

- **Commit**: `fix(docs/er): eliminar '(aprox.)' innecesario y referencia a script regenerate-erd (O6)`

#### O8 · Coordinación entre sql/ académico y api/migrations/ + DROP CASCADE

- **Archivos**:
  - `README.md` (añadir nota en sección "Paso 6" sobre coordinación)
  - `sql/04-migracion/01-staging-a-normalizado.sql` (comentar la
    decisión del `DROP TABLE servidores_publicos CASCADE` final)

- **README.md "Paso 6" — texto actual** (líneas 216-227):

  ```markdown
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
  ```

- **README.md "Paso 6" — texto propuesto** (añadir nota
  inmediatamente después del bloque, antes de "### Paso 7"):

  ```markdown
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
  ```

- **04-migracion/01 — texto actual** (línea 105-108):

  ```sql
  -- ------------------------------------------------------------
  -- Paso 6 — Drop de la tabla staging (una vez verificada la migración)
  -- ------------------------------------------------------------

  DROP TABLE servidores_publicos CASCADE;
  ```

- **04-migracion/01 — texto propuesto** (ampliar el comentario para
  documentar la decisión):

  ```sql
  -- ------------------------------------------------------------
  -- Paso 6 — Drop de la tabla staging (una vez verificada la migración)
  --
  -- Después de este DROP, las consultas de `sql/02-exploracion/*.sql`
  -- (Etapa 2) ya no podrán ejecutarse contra esta base: dependen de
  -- la tabla `servidores_publicos` desnormalizada. Los outputs de
  -- esas exploraciones ya están preservados en
  -- `evidencias/consultas-resultados/02-exploracion/`. Si necesitas
  -- re-ejecutarlas, restaura el dump físico en una base separada.
  -- ------------------------------------------------------------

  DROP TABLE servidores_publicos CASCADE;
  ```

- **Commit**: `fix(README,sql/04): aclarar coordinación entre sql/ académico y api/migrations/ + documentar drop staging (O8)`

#### O9 · docs/05-api-fastapi.md (omisión migraciones 006/007)

- **Archivo**: `docs/05-api-fastapi.md`
- **Línea afectada**: 20-21 (cuenta de migraciones)
- **Texto actual**:

  > "- 7 migraciones SQL en `api/migrations/` (alineadas con los scripts
  >   académicos de `sql/`)"

- **Texto propuesto** (documentar omisión explícita de 006/007):

  > "- 6 migraciones SQL forward + 1 rollback en `api/migrations/`,
  >   numeradas 001-005 + 008 (las migraciones 006 y 007 del backend
  >   completo tocaban datasets fuera del scope CDMX —ENIGH y
  >   CONSAR— y se omiten intencionalmente de este snapshot
  >   académico)."

- **Commit**: `fix(docs/05): documentar omisión de migraciones 006/007 (fuera de scope CDMX) (O9)`

### 3.5 — NO MODIFICAR

#### O7 · evidencias/consultas-resultados/02-exploracion/04-duplicados-categoricos.txt

- **Decisión del CEO**: NO modificar. El output preserva los 10
  cuartetos con más nombramientos en el padrón. Defendible porque:
  (a) el dataset oficial ya los publica, (b) son los 10 con más
  duplicados (consulta agregada documentada, no muestra aleatoria),
  (c) el compromiso académico de cero re-publicación fila a fila se
  refiere a publicación masiva desde la API del observatorio, no a
  10 filas concretas en una consulta exploratoria documentada
  académicamente.

---

## 4. Orden de aplicación

| Sub-fase | Contenido | Commits esperados | Pausa CEO |
|---|---|---|---|
| 1 | Plan al CEO (este documento) | 1 (`docs(internal)`) | **SÍ** — pausar al final |
| 2 | Triada principal B1 + V1 + V2 | 5 (README + docs/01 + docs/eticas + docs/02 + docs/03) | **SÍ** — pausar al final |
| 3 | V3-V6 | 4 (README + api/README + api/main.py + migrations/005) | No |
| 4 | O1-O9 (excepto O7) | ~7-8 (agrupados por archivo o por hallazgo) | No |
| 5 | Verificaciones finales consolidadas | 0 commits — sólo grep + build | No |
| 6 | PR formal al CEO | 0 commits — solo gh pr create | No |
| 7 | Reporte final al CEO | 0 commits — solo mensaje en chat | **FIN** |

Conteo total esperado de commits en `fix/peer-review-corrections`:
**17-18** (1 plan + 5 triada + 4 V3-V6 + ~7-8 observaciones).

---

## 5. Verificaciones previstas

### Pre-commit en CADA commit

Verificación grep AI signatures (obligatoria antes de cada `git commit`):

```bash
git diff --cached | grep -iE \
  "claude|anthropic|generated with|generated by|co-authored.*claude|🤖|AI[- ]?assist|made with claude|cursor|copilot|codeium"
```

Esperado: 0 matches. Si emerge match, **no commitear** y corregir.

### Verificaciones consolidadas finales (Sub-fase 5)

```bash
# 1. Cero firmas AI en todo el working tree (excepto disciplina-academica.md
#    que describe meta-textualmente la política — esto es defendible)
grep -rniE "claude|anthropic|co-authored.*claude|🤖|generated with claude|made with claude" \
  --include="*.md" --include="*.py" --include="*.sql" --include="*.toml" \
  --exclude-dir=node_modules --exclude-dir=.git .

# 2. Cero secrets
grep -rniE "npg_[A-Za-z0-9]{20,}|postgres://[^@]+:[^@]+@[^/]+|gh[ps]_[A-Za-z0-9]{36,}" \
  --include="*.py" --include="*.sql" --include="*.md" --include="*.toml" \
  --exclude-dir=node_modules --exclude-dir=.git .

# 3. Cifras corregidas consistentes
grep -rn "51,710" --include="*.md" .
grep -rn "246,490" --include="*.md" .
grep -rn "150,000" --include="*.md" .   # esperado: 0
grep -rn "150K personas" --include="*.md" .   # esperado: 0
grep -rn "miles de casos" --include="*.md" .   # esperado: 0 (post V2)
grep -rn "16 preguntas" --include="*.md" .   # esperado: 0 (post V3)

# 4. Build verde de la API (opcional, valida que pyproject.toml sigue resolviendo)
cd api/ && uv sync 2>&1 | tail -5 && cd ..
```

---

## 6. Notas operativas

- Branch dedicada: `fix/peer-review-corrections`. NO se mergea a
  `main` directamente; el merge lo decide el CEO tras revisar el PR.
- Repo permanece PRIVATE durante toda la operación.
- Las reformulaciones académicas de la triada B1+V1+V2 se aplican
  **literalmente** según los textos del prompt operacional original.
  Si emerge ambigüedad sobre el texto a aplicar, pausar y consultar
  al CEO.
- Cada commit individual pasa la verificación grep de firmas AI
  antes del `git commit`. La verificación está documentada también
  en `docs/disciplina-academica.md` como política permanente.

---

## 7. Estado actual

Documento creado: 2026-05-25.
Branch: `fix/peer-review-corrections` (HEAD parte de `19299cd` en
`main`).
Sub-fase activa: 1.
Próxima acción: commit este plan, push, reportar al CEO, pausar.
