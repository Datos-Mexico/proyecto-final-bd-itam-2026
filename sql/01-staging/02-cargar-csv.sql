-- ============================================================
-- sql/01-staging/02-cargar-csv.sql
--
-- Carga preliminar del Padrón CDMX desde el CSV original.
--
-- El CSV original contiene una fila por nombramiento vigente al
-- corte de la publicación. Los catálogos (`cat_puestos`,
-- `cat_sectores`, `cat_tipos_*`, `cat_universos`) se pueblan a
-- partir de las descripciones literales del CSV, y `servidores_publicos`
-- referencia esos catálogos por FK.
--
-- ESTE SCRIPT ES DOCUMENTAL. La carga histórica del observatorio se
-- ejecutó en abril de 2026 en plano físico desde el CSV original; el
-- estado resultante quedó preservado en el dump
-- `api/remuneraciones_cdmx.dump`. Reproducir la carga desde el CSV
-- requiere descargar el archivo del Portal de Datos Abiertos del
-- Gobierno de la Ciudad de México.
-- ============================================================

-- ------------------------------------------------------------
-- Paso 1 — Crear tabla intermedia desnormalizada
--
-- El CSV publica los catálogos como descripciones literales en cada
-- fila, no como claves. Se carga primero a una tabla intermedia para
-- normalizar después.
-- ------------------------------------------------------------

CREATE TEMP TABLE servidores_csv_raw (
    nombre               VARCHAR(200),
    apellido_1           VARCHAR(200),
    apellido_2           VARCHAR(200),
    sexo                 VARCHAR(20),
    edad                 INTEGER,
    puesto               VARCHAR(500),
    tipo_nomina          VARCHAR(100),
    tipo_contratacion    VARCHAR(100),
    tipo_personal        VARCHAR(100),
    universo             VARCHAR(200),
    sector_clave         VARCHAR(20),
    sector_nombre        VARCHAR(500),
    nivel_salarial       INTEGER,
    sueldo_bruto         NUMERIC(12,2),
    sueldo_neto          NUMERIC(12,2)
);

-- ------------------------------------------------------------
-- Paso 2 — Copiar el CSV (ajustar path local antes de ejecutar)
--
-- Comando equivalente al ejecutado históricamente en 2026-04-20:
--
--   \copy servidores_csv_raw FROM 'padron-cdmx.csv' WITH (
--       FORMAT csv,
--       HEADER true,
--       DELIMITER ',',
--       ENCODING 'UTF8'
--   );
-- ------------------------------------------------------------

-- ------------------------------------------------------------
-- Paso 3 — Poblar catálogos desde la tabla intermedia
-- ------------------------------------------------------------

INSERT INTO cat_puestos (nombre)
SELECT DISTINCT puesto FROM servidores_csv_raw
WHERE puesto IS NOT NULL
ORDER BY puesto;

INSERT INTO cat_sectores (clave, nombre)
SELECT DISTINCT sector_clave, sector_nombre FROM servidores_csv_raw
WHERE sector_nombre IS NOT NULL
ORDER BY sector_nombre;

INSERT INTO cat_tipos_contratacion (nombre)
SELECT DISTINCT tipo_contratacion FROM servidores_csv_raw
WHERE tipo_contratacion IS NOT NULL
ORDER BY tipo_contratacion;

INSERT INTO cat_tipos_personal (nombre)
SELECT DISTINCT tipo_personal FROM servidores_csv_raw
WHERE tipo_personal IS NOT NULL
ORDER BY tipo_personal;

INSERT INTO cat_universos (nombre)
SELECT DISTINCT universo FROM servidores_csv_raw
WHERE universo IS NOT NULL
ORDER BY universo;

-- Para `cat_tipos_nomina` el CSV publica el tipo como número entero;
-- se transforma directamente a la tabla.
INSERT INTO cat_tipos_nomina (clave)
SELECT DISTINCT CAST(tipo_nomina AS INTEGER) FROM servidores_csv_raw
WHERE tipo_nomina IS NOT NULL
ORDER BY 1;

-- ------------------------------------------------------------
-- Paso 4 — Insertar nombramientos referenciando catálogos
-- ------------------------------------------------------------

INSERT INTO servidores_publicos (
    nombre, apellido_1, apellido_2, sexo, edad,
    puesto_id, tipo_nomina_id, tipo_contratacion_id,
    tipo_personal_id, universo_id, sector_id,
    id_nivel_salarial, sueldo_bruto, sueldo_neto
)
SELECT
    r.nombre, r.apellido_1, r.apellido_2, r.sexo, r.edad,
    cp.id, ctn.id, ctc.id,
    ctp.id, cu.id, cs.id,
    r.nivel_salarial, r.sueldo_bruto, r.sueldo_neto
FROM servidores_csv_raw r
LEFT JOIN cat_puestos             cp  ON cp.nombre  = r.puesto
LEFT JOIN cat_tipos_nomina        ctn ON ctn.clave  = CAST(r.tipo_nomina AS INTEGER)
LEFT JOIN cat_tipos_contratacion  ctc ON ctc.nombre = r.tipo_contratacion
LEFT JOIN cat_tipos_personal      ctp ON ctp.nombre = r.tipo_personal
LEFT JOIN cat_universos           cu  ON cu.nombre  = r.universo
LEFT JOIN cat_sectores            cs  ON cs.nombre  = r.sector_nombre;

DROP TABLE servidores_csv_raw;
