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
| [`sql/02-exploracion/02-rango-fechas.sql`](../sql/02-exploracion/02-rango-fechas.sql) | Rango temporal y distribución por década. |
| [`sql/02-exploracion/03-estadisticas-numericas.sql`](../sql/02-exploracion/03-estadisticas-numericas.sql) | Media, desviación, percentiles de edad y sueldos. |
| [`sql/02-exploracion/04-duplicados-categoricos.sql`](../sql/02-exploracion/04-duplicados-categoricos.sql) | Detección de personas físicas con múltiples nombramientos. |
| [`sql/02-exploracion/05-distribucion-categorica.sql`](../sql/02-exploracion/05-distribucion-categorica.sql) | Frecuencias relativas de sexo, tipos, sectores top. |
| [`sql/02-exploracion/06-valores-nulos.sql`](../sql/02-exploracion/06-valores-nulos.sql) | Conteo y porcentaje de NULL por columna. |
| [`sql/02-exploracion/07-inconsistencias.sql`](../sql/02-exploracion/07-inconsistencias.sql) | Detección de violaciones semánticas (edad <15, sueldos negativos, neto>bruto, fechas futuras, nombres ultracortos). |

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

**Cero valores NULL en las 15 columnas no-PK** del staging. El
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
| `fecha_ingreso > CURRENT_DATE` | 0 | 0 |
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
