# Capa 03 — Esquema normalizado a 4NF

## Propósito académico

Esta capa corresponde a la **Etapa 3 de la rúbrica**: normalización
hasta 4NF. El DDL aquí versionado completa el esquema final del
proyecto académico, añadiendo los dos catálogos que faltaban en la
capa de staging (`cat_sexos`, `cat_niveles_salariales`) y separando
los datos identitarios (`personas`) de los datos de relación laboral
(`nombramientos`) — una decisión motivada empíricamente por el
hallazgo de cuartetos identitarios repetidos en la capa de
exploración (ver `sql/02-exploracion/04-duplicados-categoricos.sql`
y `evidencias/consultas-resultados/04-duplicados-categoricos.txt`).

## Decisiones de normalización aplicadas

| Capa  | Cumplimiento | Justificación |
|---|---|---|
| 1NF   | ✓ (desde staging) | Atomicidad de todas las columnas. |
| 2NF   | ✓ (desde staging) | PK simple (`id`) en `servidores_publicos`. |
| 3NF   | ✓ (nuevo en esta capa) | Catalogación de `sexo` y `nivel_salarial`. |
| BCNF  | ✓ | No hay dependencias funcionales entre atributos no-clave. |
| 4NF   | ✓ | Separación `personas`/`nombramientos` elimina dependencias multivaluadas implícitas (una persona puede tener N nombramientos). |

## Cobertura del esquema final

10 tablas:

1. `cat_sexos` — catálogo recién creado.
2. `cat_niveles_salariales` — catálogo recién creado (FK desde `nombramientos`).
3. `cat_puestos` — heredado de staging.
4. `cat_sectores` — heredado de staging.
5. `cat_tipos_contratacion` — heredado de staging.
6. `cat_tipos_nomina` — heredado de staging.
7. `cat_tipos_personal` — heredado de staging.
8. `cat_universos` — heredado de staging.
9. `personas` — tabla nueva, datos identitarios estables.
10. `nombramientos` — tabla nueva, una fila por relación laboral.

Plus 5 materialized views agregadas (`mv_dashboard_*`) que aceleran
los endpoints de dashboard de la API en la Etapa 5.
