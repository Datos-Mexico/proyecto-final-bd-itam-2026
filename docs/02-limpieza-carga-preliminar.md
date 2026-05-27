# Etapa 2 — Limpieza y carga preliminar

## Resumen ejecutivo

Esta etapa carga el Padrón CDMX en una tabla de staging
desnormalizada (`servidores_publicos`) con seis catálogos auxiliares
extraídos (`cat_puestos`, `cat_sectores`, `cat_tipos_contratacion`,
`cat_tipos_nomina`, `cat_tipos_personal`, `cat_universos`) y ejecuta
siete consultas exploratorias para caracterizar el dataset antes de
normalizar.

El estado raw pre-normalización está preservado físicamente en el
dump `remuneraciones_cdmx.dump` (PostgreSQL custom format, 4.8 MB,
fecha 2026-04-20 16:16 CST). Este repo extrae el DDL desde ese dump
y reproduce las consultas exploratorias contra los datos
restaurados localmente — cualquier persona con acceso al dump y
PostgreSQL local puede recrear los outputs.

## Scripts versionados

| Archivo | Función |
|---|---|
| [`sql/01-staging/01-create-staging.sql`](../sql/01-staging/01-create-staging.sql) | DDL de la tabla de staging y los 6 catálogos. |
| [`sql/01-staging/02-cargar-csv.sql`](../sql/01-staging/02-cargar-csv.sql) | Script referencial de carga desde el CSV original (COPY + poblado de catálogos). |
| [`sql/02-exploracion/01-valores-unicos.sql`](../sql/02-exploracion/01-valores-unicos.sql) | Conteo de valores distintos por columna. |
| [`sql/02-exploracion/03-estadisticas-numericas.sql`](../sql/02-exploracion/03-estadisticas-numericas.sql) | Media, desviación, percentiles de edad y sueldos. |
| [`sql/02-exploracion/04-duplicados-categoricos.sql`](../sql/02-exploracion/04-duplicados-categoricos.sql) | Detección de personas físicas con múltiples nombramientos. |
| [`sql/02-exploracion/05-distribucion-categorica.sql`](../sql/02-exploracion/05-distribucion-categorica.sql) | Frecuencias relativas de sexo, tipos, sectores top. |
| [`sql/02-exploracion/06-valores-nulos.sql`](../sql/02-exploracion/06-valores-nulos.sql) | Conteo y porcentaje de NULL por columna. |
| [`sql/02-exploracion/07-inconsistencias.sql`](../sql/02-exploracion/07-inconsistencias.sql) | Detección de violaciones semánticas (edad <15, sueldos negativos, neto>bruto, nombres ultracortos). |
| [`sql/02-exploracion/08-columnas-redundantes.sql`](../sql/02-exploracion/08-columnas-redundantes.sql) | Evaluación de dependencias funcionales entre columnas del staging para detectar redundancias residuales. |

## Outputs reales capturados

Todos los outputs están versionados en
`evidencias/consultas-resultados/02-exploracion/` con encabezado de
fecha, DB y archivo ejecutado.

### Valores únicos

(extracto de [`01-valores-unicos.txt`](../evidencias/consultas-resultados/02-exploracion/01-valores-unicos.txt))

- 246,821 filas totales.
- 51,710 strings distintos en `nombre` (universo léxico de primeros
  nombres como `JUAN`, `MARÍA`), no del número de personas físicas:
  la evidencia empírica sobre el cuarteto identitario `(nombre, ap1,
  ap2, edad)` muestra 246,490 cuartetos únicos sobre 246,821 filas
  (99.87%), indicando duplicación marginal.
- 1,772 puestos distintos — la columna `puesto` es claramente
  catalogable (cardinalidad baja relativa al total).
- Sólo 3 valores en `sexo` (MASCULINO, FEMENINO, NA).

## Rango de Fechas

El dataset oficial "Remuneraciones al personal de la Ciudad de México"
publicado por la Secretaría de Administración y Finanzas (SAF) del
Gobierno de la Ciudad de México en el Portal de Datos Abiertos no
contiene columnas de naturaleza temporal (fechas, marcas de tiempo,
periodos). Las 17 columnas del CSV oficial son atributos identitarios
(nombre, apellidos, sexo, edad), administrativos (puesto, sector,
tipo de nómina, universo laboral, nivel salarial) y económicos
(sueldo bruto, sueldo neto). El análisis "Rango de Fechas" de la
rúbrica de Etapa 2 no aplica a este dataset por ausencia de
atributos temporales en la fuente oficial.

### Estadísticas numéricas

(extracto de [`03-estadisticas-numericas.txt`](../evidencias/consultas-resultados/02-exploracion/03-estadisticas-numericas.txt))

| Columna | n | Media | Desv. est. | Min | P25 | Mediana | P75 | Max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| edad | 246,821 | 42.48 | 9.39 | 16 | 36 | 41 | 50 | 60 |
| sueldo_bruto | 246,821 | 13,225.32 | 9,094.33 | 461.00 | 8,115.00 | 10,410.00 | 16,451.00 | 111,178.00 |
| sueldo_neto | 246,821 | 11,796.00 | 7,142.09 | 859.17 | 7,549.19 | 9,594.49 | 14,605.06 | 83,013.92 |

Observaciones académicas:
- La media salarial está significativamente arriba de la mediana,
  consistente con distribución sesgada de cola larga (algunos
  servidores con sueldos altos elevan la media).
- El sueldo bruto máximo de $111,178 corresponde al cargo de Jefe
  de Gobierno de la CDMX (confirmado en `evidencias/consultas-resultados/05-analisis/03-ranking-puestos-window.txt`).

### Duplicados categóricos

(extracto de [`04-duplicados-categoricos.txt`](../evidencias/consultas-resultados/02-exploracion/04-duplicados-categoricos.txt))

El cuarteto identitario `(nombre, apellido_1, apellido_2, edad)`
aparece más de una vez en 305 casos (636 filas, 0.26% del padrón).
La duplicación cuarteto es marginal y probablemente representa
homónimos genuinos (personas distintas con mismo nombre, apellidos
y edad). Sin acceso a CURP/RFC no es posible determinar con
certeza si los 305 cuartetos repetidos corresponden a homónimos o
a la misma persona en múltiples nombramientos.

La decisión académica de normalizar a 4NF separando `personas` y
`nombramientos` se justifica empíricamente NO por una duplicación
masiva que el padrón no exhibe, sino por: (a) separar entidades
léxicas (nombres, apellidos) de tabuladores administrativos del
nombramiento; (b) reducir redundancia textual (51,710 strings en
catálogo reutilizable + 246,821 referencias FK vs 246,821 strings
repetidos); (c) dejar el esquema estructuralmente listo para una
futura deduplicación de personas si se obtiene acceso a un
identificador único.

### Valores nulos

(extracto de [`06-valores-nulos.txt`](../evidencias/consultas-resultados/02-exploracion/06-valores-nulos.txt))

**Cero valores NULL en las 14 columnas no-PK** del staging. El
dataset está completamente lleno. Esto incluye `apellido_2`, lo que
sugiere que los servidores sin segundo apellido aparecen con string
vacío en el CSV original — un detalle académico para documentar al
adjudicar `NOT NULL` vs `NULL` en el esquema normalizado.

### Inconsistencias semánticas

(extracto de [`07-inconsistencias.txt`](../evidencias/consultas-resultados/02-exploracion/07-inconsistencias.txt))

| Regla | Filas | % |
|---|---:|---:|
| `sueldo_neto > sueldo_bruto` | **11,426** | **4.63%** |
| `edad < 15` | 0 | 0 |
| `edad > 90` | 0 | 0 |
| `sueldo_bruto <= 0` | 0 | 0 |
| `sueldo_neto <= 0` | 0 | 0 |
| `nombre LENGTH < 2` | 0 | 0 |

**Hallazgo crítico**: 11,426 filas (4.63% del padrón) presentan
`sueldo_neto > sueldo_bruto`. Esto es semánticamente inesperado en
el modelo clásico de nómina (descuentos hacen que neto sea menor
que bruto), pero ocurre en la práctica cuando se aplican bonos,
compensaciones especiales, o pagos retroactivos en el periodo de
nómina cubierto. Esta inconsistencia se documenta como **caveat
académico** y se preserva en el esquema final (no se filtra ni se
corrige) por respeto a la fidelidad del dataset oficial. La sección
de [consideraciones éticas](consideraciones-eticas.md) discute el
trade-off entre limpieza y fidelidad.

## Columnas Redundantes

(extracto de [`08-columnas-redundantes.txt`](../evidencias/consultas-resultados/02-exploracion/08-columnas-redundantes.txt))

### Alcance del análisis

Este análisis se ejecuta sobre la tabla `servidores_publicos` del
staging preservado en el dump físico custodiado por el equipo técnico
fundador (`api/remuneraciones_cdmx.dump`, 2026-04-20 16:16 CST),
**no** sobre el CSV crudo del Portal de Datos Abiertos del Gobierno
de la CDMX. La razón es operacional: el dump físico ya tiene los
catálogos `puesto`, `sector`, `tipo_nomina`, `tipo_contratacion`,
`tipo_personal` y `universo` extraídos como FK ids (`puesto_id`,
`sector_id`, `tipo_nomina_id`, `tipo_contratacion_id`,
`tipo_personal_id`, `universo_id`). Las redundancias clave-descriptor
del CSV crudo (por ejemplo `id_universo` vs `n_universo`) ya quedaron
resueltas en la extracción inicial de catálogos. Este análisis evalúa
las dependencias funcionales que permanecen entre las columnas FK y
entre FK y valores numéricos del staging.

### Metodología

Se evalúan cuatro dependencias funcionales candidatas. Para cada par
clave→valor se compara `COUNT(DISTINCT clave)` con
`COUNT(DISTINCT (clave, valor))`: si ambos coinciden, el valor es
funcionalmente derivable de la clave (redundante); si difieren, la
clave admite varios valores distintos (no redundante).

Las cuatro dependencias evaluadas:

1. `tipo_nomina_id → tipo_contratacion_id` — ¿el tipo de nómina determina el tipo de contratación?
2. `puesto_id → id_nivel_salarial` — validación empírica de DF3 declarada como sospecha en [`dependencias-funcionales.md`](dependencias-funcionales.md).
3. `id_nivel_salarial → (sueldo_bruto, sueldo_neto)` — ¿el nivel salarial determina los sueldos exactos?
4. `puesto_id → (sueldo_bruto, sueldo_neto)` — ¿el puesto determina los sueldos directamente?

### Hallazgos empíricos

| # | Dependencia evaluada | Cardinalidad clave | Cardinalidad valor | Combinaciones únicas | Conclusión |
|---|---|---:|---:|---:|---|
| 1 | `tipo_nomina_id → tipo_contratacion_id` | 7 | 7 | 7 | **REDUNDANTE** |
| 2 | `puesto_id → id_nivel_salarial` | 1,772 | 721 | 2,285 | NO redundante |
| 3 | `id_nivel_salarial → (sueldo_bruto, sueldo_neto)` | 721 | 859 | 957 | NO redundante |
| 4 | `puesto_id → (sueldo_bruto, sueldo_neto)` | 1,772 | 859 | 2,630 | NO redundante |

**Interpretación**:

- **Q1 confirma redundancia funcional**: los 7 tipos de nómina del
  padrón mapean 1:1 con los 7 tipos de contratación. En el staging
  ambas columnas siempre coinciden, por lo que `tipo_contratacion_id`
  es derivable de `tipo_nomina_id` (o viceversa). Esta es una
  redundancia residual no resuelta en la extracción inicial de
  catálogos.
- **Q2 refuta empíricamente DF3**: el documento
  [`dependencias-funcionales.md`](dependencias-funcionales.md) declara
  `puesto → nivel_salarial` como "sospecha empírica" motivada por los
  15 puestos top con sueldos exactos repetidos por banda. La medición
  contra los 1,772 puestos completos del padrón muestra 2,285
  combinaciones únicas (≈1.29 niveles por puesto en promedio), por lo
  que la dependencia funcional **no se cumple universalmente**.
- **Q3 muestra variación intra-nivel**: el mismo `id_nivel_salarial`
  admite 957 combinaciones distintas de sueldos sobre 721 niveles
  (≈1.33 pares de sueldos por nivel). El tabulador del nivel no
  determina exactamente los sueldos publicados.
- **Q4 muestra variación intra-puesto**: el mismo `puesto_id` admite
  2,630 combinaciones distintas de sueldos sobre 1,772 puestos
  (≈1.48 pares de sueldos por puesto). El puesto no determina
  exactamente los sueldos publicados, consistente con la realidad
  observada de que servidores en el mismo puesto perciben sueldos
  distintos por antigüedad u otros factores.

### Conexión con normalización 4NF

El hallazgo Q1 (redundancia `tipo_nomina_id ↔ tipo_contratacion_id`)
**no estaba documentado** en
[`dependencias-funcionales.md`](dependencias-funcionales.md) como DF
identificada. Es una observación emergente de este análisis: en
iteraciones futuras del esquema podría consolidarse a una sola columna
con reducción adicional de redundancia. En el esquema 4NF actual ambas
columnas se preservan como FK independientes a sus catálogos
respectivos por fidelidad a la estructura del CSV oficial, que las
publica como conceptos distintos.

Los hallazgos Q2, Q3 y Q4 validan empíricamente que **la separación
ya aplicada en el esquema 4NF es correcta**: las columnas
`puesto_id`, `id_nivel_salarial`, `sueldo_bruto` y `sueldo_neto`
contienen información independiente entre sí. La sospecha de DF3
(`puesto → nivel_salarial`) declarada en
[`dependencias-funcionales.md`](dependencias-funcionales.md) se
documenta ahora como **refutada empíricamente** por la medición sobre
los 1,772 puestos completos.

### Conclusión académica

El esquema 4NF actual está correctamente justificado por las
dependencias funcionales reales del padrón. La única redundancia
residual detectada (`tipo_nomina_id ↔ tipo_contratacion_id`) queda
documentada como deuda académica menor para iteraciones futuras, sin
afectar la corrección del modelo actual.

## Conclusiones para la Etapa 3

Las exploraciones motivan empíricamente las siguientes decisiones
de normalización a 4NF:

1. **Catalogación de `sexo` y `nivel_salarial`** — ambas columnas
   son claramente catálogos (3 y 721 valores distintos
   respectivamente). La capa 03 las extrae.
2. **Separación `personas` / `nombramientos`** — el padrón publica
   una fila por nombramiento vigente, no una fila por persona.
   Aunque empíricamente la duplicación cuarteto es marginal (0.26%),
   el split académicamente correcto separa entidades léxicas
   (nombre, apellidos, sexo, edad) de los atributos laborales del
   nombramiento, reduce redundancia textual, y deja el esquema
   preparado para integrar deduplicación futura si se obtiene un
   identificador único como CURP o RFC.
3. **Documentación de caveats** — el 4.63% de inconsistencias
   `neto > bruto` se preserva pero se documenta en el diccionario.
