# Etapa 3 — Normalización hasta 4NF

## Resumen ejecutivo

Esta etapa transforma el estado raw de staging (tabla
`servidores_publicos` desnormalizada con seis catálogos extraídos)
al esquema final 4NF compuesto por **diez tablas**: `personas`,
`nombramientos`, y ocho catálogos. La transformación está
empíricamente justificada por los hallazgos de la Etapa 2 (cuartetos
identitarios repetidos, `sexo` y `nivel_salarial` con baja
cardinalidad).

## Punto de partida (capa staging)

La capa de staging (Etapa 2) entrega un estado con:

- Tabla principal `servidores_publicos` con 16 columnas (incluye
  `nombre`, `apellido_1`, `apellido_2`, `sexo`, `edad` —
  identitarios — y atributos del nombramiento).
- Seis catálogos: `cat_puestos`, `cat_sectores`,
  `cat_tipos_contratacion`, `cat_tipos_nomina`,
  `cat_tipos_personal`, `cat_universos`.
- Dos columnas pendientes de catalogación: `sexo` (string repetido)
  y `id_nivel_salarial` (integer suelto sin tabla referida).

## Análisis de niveles de normalización

| Nivel | Cumple staging | Cumple 4NF |
|---|---|---|
| 1NF (atomicidad) | ✓ — todas las columnas atómicas, sin atributos multivaluados nativos. | ✓ |
| 2NF (eliminación de dependencias parciales) | ✓ — PK simple (`id`), trivialmente cumple. | ✓ |
| 3NF (eliminación de dependencias transitivas) | ✗ — `sexo` es texto literal repetido, `id_nivel_salarial` no tiene tabla referida. | ✓ — se crean `cat_sexos` y `cat_niveles_salariales`. |
| BCNF (cada determinante es superclave) | ✗ — la dependencia `{nombre, apellido_1, apellido_2, edad} → identidad estable` co-existe con el atributo `id` (superclave). | ✓ — el split a `personas` elimina la coexistencia. |
| 4NF (eliminación de dependencias multivaluadas) | ✗ — `persona → {nombramiento_1, nombramiento_2, …}` es dependencia multivaluada implícita. | ✓ — `nombramientos` es tabla puente. |

## Dependencias funcionales y multivaluadas identificadas

Documentadas en detalle en
[`dependencias-funcionales.md`](dependencias-funcionales.md).

Sumario:

- **DF identitaria estable**:
  `{nombre, apellido_1, apellido_2, edad} → {sexo}`. La identidad
  de una persona física determina su sexo.
- **DF de catálogos**: cada FK determina los atributos
  descriptivos del catálogo (e.g. `puesto_id → {nombre del puesto}`,
  `sector_id → {clave, nombre del sector}`).
- **Dependencia multivaluada**: `persona → nombramientos`. Una
  persona puede tener N nombramientos. La normalización a 4NF
  separa este 1:N en dos tablas (`personas` y `nombramientos` con
  FK `persona_id`).

## Esquema final 4NF

10 tablas en el schema `cdmx` (cuando se aplica la migración
multischema del backend) o en `public` (default local).

### Tablas de datos

1. **`personas`** — datos identitarios estables.
   - `id` (PK)
   - `nombre`, `apellido_1`, `apellido_2`
   - `sexo_id` (FK → `cat_sexos.id`)
   - `edad`

2. **`nombramientos`** — datos de la relación laboral.
   - `id` (PK)
   - `persona_id` (FK → `personas.id`, NOT NULL)
   - `puesto_id`, `sector_id`, `tipo_nomina_id`,
     `tipo_contratacion_id`, `tipo_personal_id`, `universo_id`,
     `nivel_salarial_id` (FKs a catálogos)
   - `fecha_ingreso`
   - `sueldo_bruto`, `sueldo_neto`

### Catálogos

3. **`cat_sexos`** — NUEVO en la capa 03. 3 valores empíricos: MASCULINO, FEMENINO, NA.
4. **`cat_niveles_salariales`** — NUEVO en la capa 03. 721 niveles.
5. **`cat_puestos`** — heredado de staging. 1,772 puestos.
6. **`cat_sectores`** — heredado de staging. 73 sectores.
7. **`cat_tipos_contratacion`** — heredado de staging. 7 tipos.
8. **`cat_tipos_nomina`** — heredado de staging. 7 tipos.
9. **`cat_tipos_personal`** — heredado de staging. 11 tipos.
10. **`cat_universos`** — heredado de staging. 27 universos.

## Diagrama entidad-relación

El diagrama Mermaid auto-generado del schema real está en
[`diagrama-entidad-relacion.md`](diagrama-entidad-relacion.md).
Versión renderizada (SVG) en `evidencias/diagrama-er.svg`.

## Verificación empírica end-to-end

La migración fue ejecutada empíricamente sobre el dump físico
restaurado localmente:

| Verificación | Esperado | Real |
|---|---|---|
| Filas en `servidores_publicos` pre-migración | ≈246,800 | **246,821** |
| Filas en `personas` post-migración | igual a staging | **246,821** |
| Filas en `nombramientos` post-migración | igual a staging | **246,821** |
| Filas en `cat_sexos` | 2 o 3 | **3** (MASCULINO, FEMENINO, NA) |
| Filas en `cat_niveles_salariales` | ≈720 | **721** |

La relación inicial 1:1 entre `personas` y `nombramientos` es
correcta porque el padrón publica una fila por nombramiento vigente;
si una persona física aparece en dos nombramientos, el split la
duplica en `personas` con dos `id` distintos (esto es una decisión
académica simplificadora — en un modelo de producción se requeriría
una clave natural para deduplicar; ver caveats abajo).

## Caveats académicos

1. **Deduplicación de personas físicas**: la migración del CSV al
   esquema normalizado **no deduplica** personas físicas con
   múltiples nombramientos. Esto es porque el CSV no provee una
   clave natural confiable (no hay CURP, RFC ni identificador
   único) y la combinación `(nombre, apellido_1, apellido_2, edad)`
   tiene falsos positivos (homónimos legítimos). En un sistema de
   producción real se aplicaría record linkage probabilístico; en
   este proyecto académico se opta por preservar 1:1 en la
   migración inicial y exponer la dependencia multivaluada como
   modelo formal (`nombramientos.persona_id` permite N→1 si futura
   deduplicación lo amerita).
2. **Inconsistencias preservadas**: el 4.63% de filas con
   `sueldo_neto > sueldo_bruto` (Etapa 2) se preserva tal cual en
   el esquema 4NF — no se filtra ni se corrige por respeto a la
   fidelidad del dataset oficial.
3. **`sexo` ternario**: el valor `NA` aparece en una sola fila del
   padrón. Se preserva en `cat_sexos` para no introducir un
   `NULL`able sólo por un dato faltante; el caveat se documenta en
   el diccionario.
