# Plan de aplicación de correcciones del audit externo

Documento interno del equipo técnico fundador. Registra la matriz completa
de cambios que se aplicarán sobre el repositorio académico en respuesta al
audit externo recibido el 2026-05-25 y validado empíricamente mediante
auto-revisión académica interna el 2026-05-26 antes de aplicar correcciones.

Branch de trabajo: `fix/audit-externo-correcciones` (parte de `6fd03cf` en
`main`). Ningún cambio toca `main` directamente; el PR formal se abre al
final.

---

## 1. Resumen ejecutivo

El audit externo identificó 7 observaciones sobre el repositorio académico
público `Datos-Mexico/proyecto-final-bd-itam-2026`. La auto-revisión
académica interna del equipo validó cada una contra evidencia empírica.
Las decisiones académicas del equipo sobre cómo aplicar las correcciones
son:

- **OBS 1** (`fecha_ingreso` sin origen documentado en fuente oficial):
  remover completamente del repo académico. El dataset oficial no contiene
  columnas temporales y el repo debe reflejar esa realidad con fidelidad.
- **OBS 2** (composición del equipo): agregar línea puente en README que
  distinga al equipo fundador del curso de la composición vigente del
  observatorio.
- **OBS 3** (atribución de trabajo): crear documento honesto sobre la
  distribución real del trabajo entre los 4 integrantes.
- **OBS 4** (`datos-mexico-site` 404): hacer público el sitio canónico tras
  verificación académicamente correcta de cero secrets en historia git.
- **OBS 5** (peer review no identificado): reformular el documento interno
  como auto-revisión académica del equipo, no como peer review externo.
- **OBS 6** (disciplina académica sobre herramientas externas de
  generación): sin cambio. La declaración actual de "cero firmas en
  artefactos del repositorio" es literalmente verdadera y se mantiene
  intacta.
- **OBS 7** (SQL faltante "Columnas Redundantes"): agregar análisis SQL
  ejecutado contra restauración local del dump físico, con output real.

Adicionalmente, hallazgo emergente de la auto-revisión interna:
- **Hallazgo emergente** (conteo de columnas 16 vs 17): corregir
  `docs/01-seleccion-dataset.md §6` para alinear con la fuente oficial
  (17 columnas del CSV oficial CDMX).

---

## 2. Inventario empírico al inicio del trabajo

Datos medidos contra el repo en `main` (HEAD `6fd03cf`) el 2026-05-26:

| Métrica | Valor |
|---|---|
| Ocurrencias totales de `fecha_ingreso` | 90 |
| Archivos con `fecha_ingreso` | 27 |
| Ocurrencias de "peer review externo" | 1 (en `docs/internal/peer-review-corrections-plan.md`) |
| Archivos con "peer review" | 1 |
| `Datos-Mexico/datos-mexico-site` visibility | PRIVATE |

Distribución de `fecha_ingreso` por categoría de archivo:

| Categoría | Archivos | Ocurrencias |
|---|---:|---:|
| `sql/01-staging/` | 2 | 4 |
| `sql/02-exploracion/` | 4 | 12 |
| `sql/03-normalizado/` | 1 | 1 |
| `sql/04-migracion/` | 1 | 3 |
| `api/migrations/` | 3 | 45 |
| `api/app/` | 6 | 10 |
| `docs/` | 5 | 9 |
| `evidencias/` | 3 | 3 |

Estado de afirmaciones a corregir:
- `docs/01-seleccion-dataset.md §6` línea 81 declara "16" columnas.
- `docs/01-seleccion-dataset.md §11` lines 142-147 describen `fecha_ingreso`
  como "única dimensión temporal del dataset".
- `docs/02-limpieza-carga-preliminar.md` no tiene actualmente sección
  "Rango de Fechas"; el rango se cubre dentro de `02-rango-fechas.sql`.
- `README.md` sección "Equipo académico" lista 4 integrantes sin línea
  puente al observatorio.
- `docs/internal/peer-review-corrections-plan.md` líneas 1 y 5 afirman
  "peer review externo" / "peer review académico externo".

---

## 3. Matriz de cambios

### 3.1 — OBS 5 — Renombrar + reformular `peer-review-corrections-plan.md`

- **Archivos afectados**:
  - `docs/internal/peer-review-corrections-plan.md` → renombrar a
    `docs/internal/auto-revision-pre-publicacion-plan.md` (git mv)
- **Líneas afectadas**: 1 (título), 5 (descripción)
- **Texto actual línea 1**:
  > "# Plan de aplicación de correcciones del peer review académico externo"
- **Texto propuesto línea 1**:
  > "# Plan de aplicación de correcciones de la auto-revisión académica interna"
- **Texto actual líneas 1-7** (encabezado completo del documento):
  > "Documento interno del equipo técnico fundador. Registra la matriz
  > completa de cambios que se aplicarán sobre el repositorio académico
  > en respuesta al peer review externo independiente ejecutado el
  > 2026-05-25, antes de hacer público el repo + invitar al profesor."
- **Texto propuesto líneas 1-7** (reformulación literal del §3.1 del prompt):
  > "Plan de aplicación de correcciones derivadas de la auto-revisión
  > académica interna del equipo previa a la publicación del repositorio
  > el 2026-05-25. Esta revisión académica fue ejecutada por el equipo
  > técnico antes de hacer público el repositorio, con criterios rigurosos
  > de validación contra la rúbrica del curso, contra la evidencia empírica
  > disponible en el repo, y contra los principios constitucionales del
  > Observatorio Datos México (transparencia 100%, replicabilidad,
  > corrección académica)."
- **Commit**: `fix(docs/internal): reformular como auto-revisión interna del equipo (OBS 5)`

### 3.2 — OBS 1 — Remoción de `fecha_ingreso` (sub-fase más extensa)

#### 3.2.1 — SQL académicos

| Archivo | Cambios |
|---|---|
| `sql/01-staging/01-create-staging.sql` | Eliminar línea `fecha_ingreso DATE,` del DDL |
| `sql/01-staging/02-cargar-csv.sql` | Eliminar `fecha_ingreso DATE,` (línea 38), y de los INSERT subsecuentes (3 referencias totales) |
| `sql/02-exploracion/01-valores-unicos.sql` | Eliminar línea 31 (`'Fechas_ingreso distintas'`) |
| `sql/02-exploracion/02-rango-fechas.sql` | **Eliminar archivo completo** |
| `sql/02-exploracion/06-valores-nulos.sql` | Eliminar referencias a `n_fecha_ingreso` (líneas 21, 38) |
| `sql/02-exploracion/07-inconsistencias.sql` | Eliminar regla `'fecha_ingreso > CURRENT_DATE'` (líneas 41-44) |
| `sql/03-normalizado/01-create-tablas-normalizadas.sql` | Eliminar línea `fecha_ingreso DATE,` |
| `sql/04-migracion/01-staging-a-normalizado.sql` | Eliminar `fecha_ingreso` de INSERT y SELECT (3 referencias) |

Evidencias a eliminar/editar:
| Archivo | Acción |
|---|---|
| `evidencias/consultas-resultados/02-exploracion/02-rango-fechas.txt` | **Eliminar archivo completo** |
| `evidencias/consultas-resultados/02-exploracion/06-valores-nulos.txt` | Eliminar fila `fecha_ingreso \| 0 \| 0.0000` |
| `evidencias/consultas-resultados/02-exploracion/07-inconsistencias.txt` | Eliminar fila `fecha_ingreso > CURRENT_DATE \| 0 \| 0.0000` |

#### 3.2.2 — API backend snapshot

| Archivo | Cambios |
|---|---|
| `api/migrations/001_normalize.sql` | Eliminar columna del CREATE TABLE y de INSERT (4 referencias en líneas 63, 71, 76, 104) |
| `api/migrations/003_indexes_and_extensions.sql` | Eliminar el bloque del índice `idx_nomb_fecha_ingreso` (líneas 40-43, 4 referencias) |
| `api/migrations/004_materialized_views.sql` | Eliminar el campo `avg_seniority` de `mv_dashboard_overview` (línea 44) y eliminar la materialized view de antigüedad completa (`mv_dashboard_seniority_buckets`, ~líneas 130-200, 36 referencias) |
| `api/app/models/servidores.py` | Eliminar `fecha_ingreso` del modelo (línea 34) |
| `api/app/schemas/servidores.py` | Eliminar del schema (línea 29) |
| `api/app/schemas/nombramientos.py` | Eliminar de los 3 schemas (`Nombramiento`, `NombramientoCreate`, `NombramientoUpdate`, líneas 16, 29, 44) |
| `api/app/dependencies.py` | Quitar de `ALLOWED_ORDER_COLUMNS` (línea 64) y de `_NOMBRAMIENTO_ORDER_COLS` (línea 69) |
| `api/app/routers/servidores.py` | Quitar del SELECT (línea 315) y del constructor de respuesta (línea 345) |
| `api/app/routers/nombramientos.py` | Eliminar del ejemplo `_NOMB_EXAMPLE` (línea 57) |

Verificar adicionalmente: `api/app/routers/dashboard.py` y
`api/app/routers/analytics.py` — si exponen `avg_seniority` o el endpoint
de seniority buckets, eliminar también.

#### 3.2.3 — Documentación

| Archivo | Cambios |
|---|---|
| `docs/01-seleccion-dataset.md` | §6 (línea 81): "16" → "17" (aplicar §3.3 del prompt). §7 (línea 108): eliminar la fila de `fecha_ingreso`. §11 (líneas 142-147): reformular completo según §3.3 del prompt |
| `docs/02-limpieza-carga-preliminar.md` | Eliminar mención del script `02-rango-fechas.sql` en la tabla de scripts (línea 26). Eliminar fila `fecha_ingreso > CURRENT_DATE` en la tabla de inconsistencias (línea 113). Agregar sección "Rango de Fechas" con el texto literal del §3.2 del prompt |
| `docs/03-normalizacion-4nf.md` | Eliminar mención de `fecha_ingreso` en la lista de columnas de `nombramientos` (línea 80) |
| `docs/diccionario-datos.md` | Eliminar fila `fecha_ingreso` de la tabla de `nombramientos` (línea 44). Eliminar de la vista de compatibilidad (línea 157) |
| `docs/diagrama-entidad-relacion.md` | Eliminar `date fecha_ingreso` (líneas 47, 153) y mención en prosa (línea 107) |
| `docs/dependencias-funcionales.md` | Eliminar de las 2 DFs/DMVs declaradas (líneas 14, 93) |

Evidencias derivadas:
- `evidencias/diagrama-er.svg`: el SVG fue generado con `mermaid-cli` u
  otro generador del bloque Mermaid de `diagrama-entidad-relacion.md`.
  **Acción requerida**: regenerar el SVG tras editar el bloque Mermaid,
  o editar manualmente el SVG. **Pregunta abierta al CEO**: ¿se prefiere
  regenerar o editar a mano?

#### 3.2.4 — Hallazgo emergente: conteo 16 → 17 columnas

`docs/01-seleccion-dataset.md` §6 línea 81 declara 16 columnas, pero la
fuente oficial CSV tiene 17 campos. Aplicar texto literal del §3.3 del
prompt para alinear con realidad de la fuente oficial.

#### 3.2.5 — Caso particular: `docs/04-analisis-resultados.md` línea 86

El doc usa la palabra "antigüedad" interpretativamente (no como variable
del análisis): *"sugiriendo que la antigüedad no es el factor dominante
en la determinación del sueldo"*. El análisis subyacente es sobre `edad`
(percentiles por grupo etario), no sobre `fecha_ingreso`. La prosa
sigue siendo válida tras remover `fecha_ingreso`.

**Decisión propuesta**: mantener la prosa tal cual (la oración no
depende de `fecha_ingreso`). Alternativa: reescribir para evitar la
palabra "antigüedad" si el CEO lo prefiere.

#### 3.2.6 — Commits granulares de remoción

```
fix(sql/01-staging): remover fecha_ingreso de staging DDL y carga CSV (OBS 1)
fix(sql/02-exploracion): eliminar 02-rango-fechas, evidencia y referencias residuales (OBS 1)
fix(sql/03-normalizado,04-migracion): remover fecha_ingreso del esquema 4NF y migración (OBS 1)
fix(api): remover fecha_ingreso de migrations, modelos, schemas y routers (OBS 1)
fix(docs/01): alinear conteo de columnas con fuente oficial y reformular series temporales (OBS 1 + hallazgo emergente)
fix(docs/02): documentar no-aplicabilidad de Rango de Fechas (OBS 1)
fix(docs): eliminar referencias residuales a fecha_ingreso en docs/03, diccionario, ER, DFs (OBS 1)
```

### 3.3 — OBS 2 — Línea puente en README sobre composición del equipo

- **Archivo**: `README.md`
- **Líneas afectadas**: tras línea 42 (final de la tabla del equipo)
- **Texto a agregar** (literal del §3.4 del prompt):
  > "El Observatorio Datos México, derivado del trabajo de este proyecto,
  > tiene actualmente una composición más amplia que incluye también
  > miembros incorporados después del cierre del entregable académico del
  > semestre. La composición vigente del observatorio se documenta en
  > [datosmexico.org/quienes-somos](https://datosmexico.org/quienes-somos).
  > Este repositorio refleja exclusivamente el equipo técnico fundador
  > que ejecutó el proyecto académico del curso COM-12101-001."
- **Commit**: `fix(README): agregar línea puente sobre composición del observatorio vs equipo del curso (OBS 2)`

### 3.4 — OBS 4 — Hacer público `datos-mexico-site`

Sub-fase con pausa obligatoria. Procedimiento:
1. Clonar `Datos-Mexico/datos-mexico-site` con history completa.
2. Ejecutar 3 verificaciones de cero secrets:
   - `git log --all -p | grep -iE "<patrones secrets>"`
   - `git log --all --oneline --diff-filter=A -- '*.env*'`
   - `grep -rE "(api[_-]?key|secret|password|token).*=.*['\"][A-Za-z0-9]{16,}"` en working tree
3. Verificar `.gitignore` cubre `.env*`.
4. Si todo limpio: pausar para autorización del CEO.
5. Tras autorización: `gh repo edit Datos-Mexico/datos-mexico-site --visibility public --accept-visibility-change-consequences`.
6. Verificar visibility=PUBLIC y HTTP 200.

### 3.5 — OBS 3 — Atribución honesta del trabajo

- **Archivo nuevo**: `docs/atribucion-equipo.md` (contenido literal del §3.5 del prompt).
- **Edición de `README.md`**: agregar línea tras la sección "Equipo académico"
  con referencia al doc:
  > "Detalles sobre la atribución de trabajo por integrante se documentan
  > en [`docs/atribucion-equipo.md`](docs/atribucion-equipo.md)."
- **Commit**: `docs: agregar atribución honesta de trabajo por integrante (OBS 3)`

### 3.6 — OBS 7 — Análisis "Columnas Redundantes" con ejecución real

- **Archivo nuevo**: `sql/02-exploracion/08-columnas-redundantes.sql`
  (contenido literal del §3.6 del prompt).
- **Procedimiento**:
  1. Restaurar dump físico a `proyecto_academico_staging_v2`.
  2. Ejecutar el script y capturar output en
     `evidencias/consultas-resultados/02-exploracion/08-columnas-redundantes.txt`.
  3. Agregar sección "Columnas Redundantes" a
     `docs/02-limpieza-carga-preliminar.md` con hallazgos reales.
  4. Dropear DB temporal.
- **Pregunta abierta al CEO**: ¿el dump físico está accesible localmente
  (mismo path que FASE 1 sub-fase 1.5)? Si no, ¿se confirma el path correcto?
- **Commit**: `feat(sql): agregar análisis de Columnas Redundantes (OBS 7 — completar cobertura de rúbrica)`

### 3.7 — OBS 6 — Sin cambio

La declaración actual en `docs/disciplina-academica.md` sobre autoría
humana exclusiva del equipo en cualquier artefacto del repositorio es
literalmente verdadera y se mantiene intacta. No se aplica modificación.

---

## 4. Orden de aplicación

| Sub-fase | Contenido | Commits esperados | Pausa CEO |
|---|---|---|---|
| 1 | Plan al CEO (este documento) | 1 (`docs(internal)`) | **SÍ** — pausar al final |
| 2 | OBS 5 (renombrar + reformular peer review doc) | 1 (`fix(docs/internal)`) | No |
| 3 | OBS 1 + hallazgo emergente (remoción `fecha_ingreso`) | 7 (granulares por categoría) | **SÍ** — pausar al final |
| 4 | OBS 2 (línea puente equipo en README) | 1 (`fix(README)`) | No |
| 5 | OBS 4 (hacer público `datos-mexico-site`) | 0 commits en este repo | **SÍ** — pausar antes del visibility change |
| 6 | OBS 3 (atribución de equipo) | 1 (`docs`) | No |
| 7 | OBS 7 (SQL Columnas Redundantes con ejecución real) | 1 (`feat(sql)`) | No |
| 8 | Verificaciones consolidadas finales + PR formal | 0 commits — solo grep + build + gh pr create | No |
| 9 | Reporte final al CEO | 0 commits — solo mensaje en chat | **FIN** |

Total esperado de commits en `fix/audit-externo-correcciones`: **~12**
(1 plan + 1 OBS 5 + 7 remoción + 1 OBS 2 + 1 OBS 3 + 1 OBS 7).

---

## 5. Verificaciones previstas

### Pre-commit en cada commit

Verificación de autoría humana exclusiva (obligatoria antes de cada `git commit`):

```bash
./scripts/verify-clean-commits.sh
```

Esperado: exit code 0. Si el script devuelve exit code 1, no commitear
y corregir.

### Verificaciones consolidadas finales (Sub-fase 8)

```bash
# 1. Cero firmas externas en todo el working tree
./scripts/verify-clean-worktree.sh

# 2. Cero referencias residuales a fecha_ingreso (fuera de docs/internal)
grep -rn "fecha_ingreso" --include="*.md" --include="*.py" --include="*.sql" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv \
  --exclude-dir=docs/internal

# 3. Cero referencias a "peer review externo"
grep -rn "peer review externo\|peer review independiente" --include="*.md" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=.venv

# 4. Verificar visibility de datos-mexico-site
gh repo view Datos-Mexico/datos-mexico-site --json visibility

# 5. Build verde de la API
cd api/ && uv sync 2>&1 | tail -5 && cd ..
```

---

## 6. Preguntas abiertas para el CEO

Estas decisiones requieren input del CEO antes/durante la aplicación:

1. **Diagrama ER SVG**: ¿se prefiere regenerar el SVG con generador
   automático tras editar el bloque Mermaid, o editar manualmente el
   SVG para remover `fecha_ingreso`?
2. **Dump físico para OBS 7**: ¿el archivo `remuneraciones_cdmx.dump`
   está disponible localmente en el path esperado
   (`/Users/davicho/datos-itam/api/remuneraciones_cdmx.dump` o
   equivalente)? Si no, ¿cuál es el path correcto?
3. **`docs/04-analisis-resultados.md` línea 86 ("antigüedad" interpretativa)**:
   ¿se mantiene la prosa tal cual (recomendación: sí, no depende de
   `fecha_ingreso`) o se reescribe para evitar la palabra "antigüedad"?
4. **Materialized views de antigüedad**: la migración 004 contiene una
   materialized view completa (`mv_dashboard_seniority_buckets`) de
   buckets de antigüedad. Al eliminarla, los endpoints `/dashboard/stats`
   pierden esa dimensión. **Decisión propuesta**: eliminar la MV completa
   (consistente con la decisión de remover `fecha_ingreso`). Confirmar.

---

## 7. Estado actual

Documento creado: 2026-05-26.
Branch: `fix/audit-externo-correcciones` (HEAD parte de `6fd03cf` en `main`).
Sub-fase activa: 1.
Próxima acción: commit este plan, push, reportar al CEO, pausar.
