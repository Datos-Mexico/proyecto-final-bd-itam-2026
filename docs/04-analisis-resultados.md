# Etapa 4 — Análisis de resultados

## Resumen ejecutivo

Esta etapa ejecuta cuatro consultas SQL analíticas avanzadas sobre
el esquema 4NF normalizado (Etapa 3) y reporta los hallazgos
sustantivos. Las consultas usan agregaciones, joins multi-tabla,
window functions (`ROW_NUMBER`, `RANK`, `DENSE_RANK`) y agregaciones
de cuantiles (`PERCENTILE_CONT WITHIN GROUP`).

Todos los outputs están versionados en
`evidencias/consultas-resultados/05-analisis/` y fueron capturados
ejecutando los scripts contra la DB local restaurada desde el dump
físico del 2026-04-20.

## Consultas ejecutadas

| Archivo | Pregunta de investigación | Output |
|---|---|---|
| [`sql/05-analisis/01-distribucion-salarial.sql`](../sql/05-analisis/01-distribucion-salarial.sql) | ¿Cómo se distribuye el padrón en cinco rangos de sueldo bruto? | [`01-distribucion-salarial.txt`](../evidencias/consultas-resultados/05-analisis/01-distribucion-salarial.txt) |
| [`sql/05-analisis/02-brecha-genero-por-sector.sql`](../sql/05-analisis/02-brecha-genero-por-sector.sql) | ¿En qué sectores con ≥100 nombramientos existe la mayor brecha salarial por sexo? | [`02-brecha-genero-por-sector.txt`](../evidencias/consultas-resultados/05-analisis/02-brecha-genero-por-sector.txt) |
| [`sql/05-analisis/03-ranking-puestos-window.sql`](../sql/05-analisis/03-ranking-puestos-window.sql) | ¿Cuáles son los 15 puestos mejor pagados y cuántas personas los ocupan, ilustrando diferencias entre `ROW_NUMBER`/`RANK`/`DENSE_RANK`? | [`03-ranking-puestos-window.txt`](../evidencias/consultas-resultados/05-analisis/03-ranking-puestos-window.txt) |
| [`sql/05-analisis/04-percentiles-por-grupo.sql`](../sql/05-analisis/04-percentiles-por-grupo.sql) | ¿Cómo varían los percentiles salariales por grupo etario y sexo? | [`04-percentiles-por-grupo.txt`](../evidencias/consultas-resultados/05-analisis/04-percentiles-por-grupo.txt) |

## Hallazgos clave

### 1. Distribución salarial muy concentrada en el rango medio-bajo

| Rango | N | Sueldo promedio | % |
|---|---:|---:|---:|
| 1. Menos de $5K | 10,924 | $3,839.61 | 4.43% |
| 2. $5K - $10K | 105,126 | $7,884.81 | 42.59% |
| 3. $10K - $20K | 101,616 | $14,517.20 | 41.17% |
| 4. $20K - $40K | 24,433 | $26,307.37 | 9.90% |
| 5. Más de $40K | 4,722 | $58,342.89 | 1.91% |

**83.76% del padrón gana menos de $20K MXN brutos mensuales.** Sólo
**1.91%** percibe más de $40K. La distribución es fuertemente
sesgada hacia el rango medio-bajo.

### 2. Brecha de género por sector

Análisis sobre 22 sectores con ≥100 nombramientos. Los 5 sectores
con mayor brecha (`(avgMale - avgFemale) / avgFemale * 100`):

| Sector | avg Masc | avg Feme | Brecha % | N |
|---|---:|---:|---:|---:|
| CAJA DE PREVISION DE LA POLICIA AUXILIAR DE LA CDMX | $17,189.77 | $13,336.00 | **+28.90%** | 144 |
| SECRETARIA DE TRABAJO Y FOMENTO AL EMPLEO EN LA CDMX | $15,082.91 | $12,444.18 | +21.20% | 595 |
| JEFATURA DE GOBIERNO DE LA CDMX | $18,877.39 | $15,667.27 | +20.49% | 554 |
| CENTRO DE COMANDO C5 | $18,549.72 | $15,478.00 | +19.85% | 487 |
| SECRETARIA DE GOBIERNO DE LA CDMX | $16,310.56 | $13,930.02 | +17.09% | 1,313 |

La brecha promedio del padrón completo es **+3.76%** (calculada
sobre la totalidad sin filtro por sector). Sin embargo, al
desagregar por sector emergen brechas significativamente más
altas, lo cual sugiere que la brecha global se ve atenuada por
sectores grandes y relativamente paritarios (e.g. Seguridad
Ciudadana con sus ~50K nombramientos diluye el promedio).

### 3. Demostración pedagógica de window functions

Los 15 puestos mejor pagados ilustran exactamente la diferencia
entre las tres funciones de ranking:

| `ROW_NUMBER` | `RANK` | `DENSE_RANK` | Puesto | Sueldo | Ocupantes |
|---:|---:|---:|---|---:|---:|
| 1 | 1 | 1 | JEFE DE GOBIERNO | $111,178 | 1 |
| 2-4 | 2 (empate) | 2 | SECRETARIO, COMISIONADO, SEC. PARTICULAR AA | $109,981 | 25 |
| 5-9 | 5 (empate) | 3 | COORDINADOR GENERAL B, ALCALDE, SUBSEC. ... | $104,740 | 47 |
| 10-13 | 10 (empate) | 4 | ASESOR D, COORD. GENERAL A, ... | $99,967 | 39 |
| 14-15 | 14 (empate) | 5 | DIRECTOR EJECUTIVO D, COORD. EJECUTIVO | $95,327 | 5 |

Hallazgo académico: en escalafones gubernamentales, los empates
salariales son la norma (tabuladores estandarizados); `RANK` deja
huecos por el número de empatadores, mientras que `DENSE_RANK`
asigna números consecutivos (1, 2, 3, 4, 5 — más útil cuando se
quiere expresar "nivel jerárquico salarial").

### 4. Percentiles por grupo etario y sexo

(Datos extraídos de `04-percentiles-por-grupo.txt`)

- **El sueldo mediano es bastante estable a través de los rangos
  etarios** (entre $9,009 y $11,147 para todos los grupos de 18-55
  años), sugiriendo que la antigüedad no es el factor dominante en
  la determinación del sueldo en la administración de la CDMX
  (probablemente domina el tabulador del puesto).
- **El P90 sí crece con la edad**: $15,275 para hombres 16-25 vs
  $24,305 para hombres 46-55 — los puestos más altos están
  dominados por servidores con más edad.
- **Una persona registrada con sexo `NA`** aparece exclusivamente
  en el rango 46-55. Es el caso único del valor ternario en
  `cat_sexos`.

> **Nota académica sobre el bucket etario más joven**: el bucket
> `1. 18-25` en el output preservado en
> `evidencias/consultas-resultados/05-analisis/04-percentiles-por-grupo.txt`
> incluye empíricamente edades 16-17 (el mínimo del padrón es 16
> años). El script SQL en
> [`sql/05-analisis/04-percentiles-por-grupo.sql`](../sql/05-analisis/04-percentiles-por-grupo.sql)
> fue corregido al label `1. 16-25` para reflejar el rango real. La
> evidencia se preserva tal cual fue capturada como artefacto
> histórico del proceso académico ejecutado en su momento; al
> re-ejecutar el script corregido, el output mostrará el nuevo
> label sin cambiar el número de filas ni los valores agregados.

## Cómo reproducir los outputs

```bash
# Restaurar dump físico
createdb proyecto_academico
pg_restore -d proyecto_academico --no-owner --no-privileges remuneraciones_cdmx.dump

# Aplicar normalización
psql -d proyecto_academico -f sql/03-normalizado/01-create-tablas-normalizadas.sql
psql -d proyecto_academico -f sql/04-migracion/01-staging-a-normalizado.sql
psql -d proyecto_academico -f sql/03-normalizado/02-create-indexes.sql

# Ejecutar las 4 consultas analíticas
for f in sql/05-analisis/*.sql; do
  psql -d proyecto_academico -f "$f"
done
```
