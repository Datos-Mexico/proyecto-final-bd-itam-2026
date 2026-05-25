# Datos crudos (instrucciones de descarga)

Este directorio no contiene CSV ni dumps en versionado git: los
archivos crudos están en `.gitignore` para mantener el repo
ligero y evitar duplicación con la fuente oficial.

## Cómo obtener el CSV original

El Padrón de Servidores Públicos de la Ciudad de México está
disponible en el **Portal de Datos Abiertos del Gobierno de la
Ciudad de México**. La forma autoritativa de acceso es la página
oficial del portal; cualquier URL específica de descarga puede
cambiar con el tiempo conforme el publicador actualice la
publicación.

Pasos sugeridos para localizar el CSV:

1. Ir al portal de datos abiertos del Gobierno de la CDMX.
2. Buscar "Padrón de Servidores Públicos" o "Remuneraciones
   CDMX".
3. Descargar el archivo CSV (formato UTF-8).
4. Colocar el archivo en este directorio como `padron-cdmx.csv`
   antes de ejecutar `sql/01-staging/02-cargar-csv.sql`.

## Cómo obtener el dump físico histórico

Alternativa de mayor fidelidad para reproducir exactamente el
estado del padrón al 2026-04-20:

El dump físico `remuneraciones_cdmx.dump` (4.8 MB, formato
PostgreSQL custom v1.15-0, snapshot del 2026-04-20 16:16 CST) es
custodiado por el equipo técnico fundador del Observatorio
Datos México y se puede solicitar directamente.

Para restaurarlo localmente:

```bash
createdb proyecto_academico
pg_restore -d proyecto_academico --no-owner --no-privileges \
  /path/to/remuneraciones_cdmx.dump
```

Una vez restaurado, todas las consultas SQL versionadas en
`sql/01-staging/*` y `sql/02-exploracion/*` son ejecutables sin
necesidad de descargar el CSV.
