# Capa 01 — Staging (carga inicial del Padrón CDMX)

## Propósito académico

Esta capa corresponde a la **Etapa 2 de la rúbrica**: limpieza y carga
preliminar del dataset. Contiene el DDL y la lógica de carga que
establecen la tabla `servidores_publicos` desnormalizada y los seis
catálogos extraídos (`cat_puestos`, `cat_sectores`,
`cat_tipos_contratacion`, `cat_tipos_nomina`, `cat_tipos_personal`,
`cat_universos`) como base para las consultas exploratorias de la capa
02 y para la posterior normalización a 4NF de la capa 03.

## Origen empírico de este DDL

El DDL versionado en `01-create-staging.sql` fue extraído del dump
físico histórico
`api/remuneraciones_cdmx.dump` preservado en la laptop del equipo
técnico fundador, con fecha de creación **2026-04-20 16:16 CST** —
formato PostgreSQL custom, 4.8 MB, schema raw pre-normalización del
observatorio.

Este estado raw conserva los seis catálogos ya extraídos del CSV
original del Padrón CDMX, lo cual técnicamente lo clasifica como
**1NF + parcialmente 2NF**: las columnas categóricas con baja
cardinalidad (puestos, sectores, tipos) viven en tablas separadas
referenciadas por FK; pero `sexo` permanece como `VARCHAR(20)`
literal en la fila de `servidores_publicos` (sin catálogo), y
`id_nivel_salarial` permanece como `INTEGER` desreferenciado, sin
tabla catálogo. La normalización a 4NF (capa 03) extrae esos dos
catálogos faltantes y particiona los datos identitarios
(`personas`) y de relación laboral (`nombramientos`).

## CSV original

El Padrón de Servidores Públicos de la Ciudad de México es un
dataset abierto publicado por la Dirección General de Administración
de Personal y Desarrollo Administrativo del Gobierno de la CDMX,
disponible en el Portal de Datos Abiertos del Gobierno de la Ciudad
de México. El archivo CSV original contiene aproximadamente 246,800
filas, una por nombramiento vigente, con columnas para nombre,
apellidos, sexo, edad, fecha de ingreso, sueldos bruto y neto, y
descripciones literales (no catalogadas) de puesto, sector,
tipo de nómina, tipo de contratación, tipo de personal, universo
laboral y nivel salarial.

## Reproducibilidad

Cualquier persona con acceso al dump físico o al CSV original puede
recrear este estado:

```bash
# Opción A — restaurar desde el dump físico (fidelidad máxima)
createdb proyecto_academico_staging
pg_restore -d proyecto_academico_staging --no-owner --no-privileges remuneraciones_cdmx.dump

# Opción B — recrear desde el CSV (requiere ejecutar 01-create-staging.sql
# y 02-cargar-csv.sql tras descargar el CSV original)
createdb proyecto_academico_staging
psql -d proyecto_academico_staging -f sql/01-staging/01-create-staging.sql
psql -d proyecto_academico_staging -c "\\copy servidores_publicos FROM 'padron-cdmx.csv' CSV HEADER"
```
