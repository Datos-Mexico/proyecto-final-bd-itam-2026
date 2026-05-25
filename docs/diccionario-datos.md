# Diccionario de datos del esquema 4NF

Documento de referencia campo por campo del esquema normalizado a
4NF aplicado al Padrón de Servidores Públicos de la CDMX. Cubre
las dos tablas de datos (`personas`, `nombramientos`) y los ocho
catálogos.

---

## Tabla `personas`

Entidad identidad. Una fila por persona física registrada en el
padrón.

| Columna | Tipo PostgreSQL | NULL | Default | Descripción |
|---|---|---|---|---|
| `id` | `SERIAL` (INTEGER auto) | NO | `nextval(...)` | Clave primaria. |
| `nombre` | `VARCHAR(200)` | NO | — | Nombre de pila. |
| `apellido_1` | `VARCHAR(200)` | NO | — | Apellido paterno. |
| `apellido_2` | `VARCHAR(200)` | YES | — | Apellido materno. Algunos servidores no tienen segundo apellido; en esos casos el campo viene vacío en el CSV original y se almacena como string vacío o NULL. |
| `sexo_id` | `INTEGER` | YES | — | FK → `cat_sexos.id`. |
| `edad` | `INTEGER` | YES | — | Edad al momento del corte del padrón. Rango empírico observado: 16-60. |

Índices: PK sobre `id`, `idx_personas_sexo_id`, `idx_personas_edad`.

---

## Tabla `nombramientos`

Entidad relación laboral. Una fila por nombramiento vigente al
corte del padrón. Una persona puede tener N nombramientos.

| Columna | Tipo PostgreSQL | NULL | Default | Descripción |
|---|---|---|---|---|
| `id` | `SERIAL` | NO | `nextval(...)` | Clave primaria. |
| `persona_id` | `INTEGER` | **NO** | — | FK → `personas.id`. Una persona → N nombramientos. |
| `puesto_id` | `INTEGER` | YES | — | FK → `cat_puestos.id`. |
| `sector_id` | `INTEGER` | YES | — | FK → `cat_sectores.id`. |
| `tipo_nomina_id` | `INTEGER` | YES | — | FK → `cat_tipos_nomina.id`. |
| `tipo_contratacion_id` | `INTEGER` | YES | — | FK → `cat_tipos_contratacion.id`. |
| `tipo_personal_id` | `INTEGER` | YES | — | FK → `cat_tipos_personal.id`. |
| `universo_id` | `INTEGER` | YES | — | FK → `cat_universos.id`. |
| `nivel_salarial_id` | `INTEGER` | YES | — | FK → `cat_niveles_salariales.id`. |
| `fecha_ingreso` | `DATE` | YES | — | Fecha de inicio del nombramiento. |
| `sueldo_bruto` | `NUMERIC(12,2)` | YES | — | Sueldo bruto mensual en MXN. Rango empírico: $461.00 - $111,178.00. |
| `sueldo_neto` | `NUMERIC(12,2)` | YES | — | Sueldo neto mensual en MXN. **Caveat académico**: el 4.63% de filas presentan `sueldo_neto > sueldo_bruto`; la inconsistencia se preserva por fidelidad al dataset oficial (ver [Etapa 2](02-limpieza-carga-preliminar.md)). |

Índices: PK sobre `id`, FK index sobre `persona_id`, índices secundarios
sobre `sector_id`, `puesto_id`, `sueldo_bruto`, `tipo_contratacion_id`,
`tipo_personal_id`, `universo_id`, `nivel_salarial_id`.

---

## Catálogo `cat_sexos`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `nombre` | `VARCHAR(20)` | NO | Etiqueta. UNIQUE. Valores empíricos: `MASCULINO`, `FEMENINO`, `NA`. |

Cardinalidad empírica: 3.

---

## Catálogo `cat_niveles_salariales`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `clave` | `INTEGER` | NO | Identificador del nivel salarial publicado en el CSV original. UNIQUE. |

Cardinalidad empírica: 721.

---

## Catálogo `cat_puestos`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `nombre` | `VARCHAR(500)` | NO | Descripción literal del puesto. UNIQUE. |

Cardinalidad empírica: 1,772.

---

## Catálogo `cat_sectores`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `clave` | `VARCHAR(20)` | YES | Clave administrativa del sector. |
| `nombre` | `VARCHAR(500)` | NO | Nombre oficial del sector / dependencia. |

Cardinalidad empírica: 73.

---

## Catálogo `cat_tipos_contratacion`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `nombre` | `VARCHAR(100)` | NO | Tipo de contratación. UNIQUE. |

Cardinalidad empírica: 7. Valores: BASE, LISTA DE RAYA BASE, HABERES, PROVISIONAL, HONORARIOS, EVENTUAL, CARACTER SOCIAL.

---

## Catálogo `cat_tipos_nomina`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `clave` | `INTEGER` | NO | Identificador numérico del tipo de nómina. UNIQUE. |

Cardinalidad empírica: 7.

---

## Catálogo `cat_tipos_personal`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `nombre` | `VARCHAR(100)` | NO | Tipo de personal. UNIQUE. |

Cardinalidad empírica: 11. Valores: SINDICALIZADOS, HABERES, CONFIANZA, ESTABILIDAD LABORAL, BASE NO SINDICALIZADO, HONORARIOS, ESTRUCTURA, INTERINATO, LISTA DE RAYA NO SINDICALIZADO, EVENTUALES, CARACTER SOCIAL.

---

## Catálogo `cat_universos`

| Columna | Tipo | NULL | Descripción |
|---|---|---|---|
| `id` | `SERIAL` | NO | PK. |
| `clave` | `VARCHAR(20)` | YES | Clave del universo laboral. |
| `nombre` | `VARCHAR(200)` | NO | Nombre del universo. |

Cardinalidad empírica: 27.

---

## Vista de compatibilidad `v_servidores_publicos`

Vista (no es tabla) creada en `sql/04-migracion/01-staging-a-normalizado.sql`
que reconstruye el shape denormalizado del CSV original mediante
joins entre `personas`, `nombramientos`, y los catálogos
`cat_sexos` y `cat_niveles_salariales`. Sirve para verificación
post-migración y para clientes que prefieran la lectura plana.

```sql
SELECT
    p.id, p.nombre, p.apellido_1, p.apellido_2,
    cs.nombre AS sexo, p.edad,
    n.puesto_id, n.tipo_nomina_id, n.tipo_contratacion_id,
    n.tipo_personal_id, n.fecha_ingreso, n.universo_id, n.sector_id,
    cns.clave AS id_nivel_salarial, n.sueldo_bruto, n.sueldo_neto
FROM personas p
JOIN nombramientos n        ON n.persona_id = p.id
LEFT JOIN cat_sexos cs      ON cs.id = p.sexo_id
LEFT JOIN cat_niveles_salariales cns ON cns.id = n.nivel_salarial_id;
```
