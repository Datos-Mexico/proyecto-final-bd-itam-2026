-- ============================================================
-- sql/01-staging/01-create-staging.sql
--
-- DDL de la capa de staging. Define los seis catálogos extraídos
-- del CSV del Padrón CDMX y la tabla principal `servidores_publicos`
-- desnormalizada (un nombramiento por fila).
--
-- Este DDL fue extraído del dump físico histórico
-- `api/remuneraciones_cdmx.dump` (PostgreSQL custom format,
-- 2026-04-20 16:16 CST) preservado en la laptop del equipo técnico
-- fundador del observatorio. Refleja el estado raw pre-normalización
-- a 4NF del proyecto académico.
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- Catálogos extraídos del CSV original (1NF + 2NF parcial)
-- ------------------------------------------------------------

CREATE TABLE cat_puestos (
    id    SERIAL PRIMARY KEY,
    nombre VARCHAR(500) NOT NULL UNIQUE
);

CREATE TABLE cat_sectores (
    id    SERIAL PRIMARY KEY,
    clave VARCHAR(20),
    nombre VARCHAR(500) NOT NULL
);

CREATE TABLE cat_tipos_contratacion (
    id    SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE cat_tipos_nomina (
    id    SERIAL PRIMARY KEY,
    clave INTEGER NOT NULL UNIQUE
);

CREATE TABLE cat_tipos_personal (
    id    SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE cat_universos (
    id    SERIAL PRIMARY KEY,
    clave VARCHAR(20),
    nombre VARCHAR(200) NOT NULL
);

-- ------------------------------------------------------------
-- Tabla principal de staging (una fila por nombramiento vigente)
-- ------------------------------------------------------------

CREATE TABLE servidores_publicos (
    id                   SERIAL PRIMARY KEY,
    nombre               VARCHAR(200) NOT NULL,
    apellido_1           VARCHAR(200) NOT NULL,
    apellido_2           VARCHAR(200),
    sexo                 VARCHAR(20)  NOT NULL,
    edad                 INTEGER,
    puesto_id            INTEGER REFERENCES cat_puestos(id),
    tipo_nomina_id       INTEGER REFERENCES cat_tipos_nomina(id),
    tipo_contratacion_id INTEGER REFERENCES cat_tipos_contratacion(id),
    tipo_personal_id     INTEGER REFERENCES cat_tipos_personal(id),
    fecha_ingreso        DATE,
    universo_id          INTEGER REFERENCES cat_universos(id),
    sector_id            INTEGER REFERENCES cat_sectores(id),
    id_nivel_salarial    INTEGER,
    sueldo_bruto         NUMERIC(12,2),
    sueldo_neto          NUMERIC(12,2)
);

-- ------------------------------------------------------------
-- Índices que aceleran las exploraciones de la capa 02
-- ------------------------------------------------------------

CREATE INDEX idx_sp_sexo                ON servidores_publicos(sexo);
CREATE INDEX idx_sp_edad                ON servidores_publicos(edad);
CREATE INDEX idx_sp_puesto_id           ON servidores_publicos(puesto_id);
CREATE INDEX idx_sp_sector_id           ON servidores_publicos(sector_id);
CREATE INDEX idx_sp_tipo_contratacion_id ON servidores_publicos(tipo_contratacion_id);
CREATE INDEX idx_sp_tipo_nomina_id      ON servidores_publicos(tipo_nomina_id);
CREATE INDEX idx_sp_tipo_personal_id    ON servidores_publicos(tipo_personal_id);
CREATE INDEX idx_sp_universo_id         ON servidores_publicos(universo_id);
CREATE INDEX idx_sp_sueldo_bruto        ON servidores_publicos(sueldo_bruto);

COMMIT;

-- ============================================================
-- Verificación post-carga (referencia, no se ejecuta automáticamente)
--
-- SELECT COUNT(*) FROM servidores_publicos;
--   -- esperado: ~246,800
--
-- SELECT 'cat_puestos' AS t, COUNT(*) FROM cat_puestos UNION ALL
-- SELECT 'cat_sectores',          COUNT(*) FROM cat_sectores UNION ALL
-- SELECT 'cat_tipos_contratacion', COUNT(*) FROM cat_tipos_contratacion UNION ALL
-- SELECT 'cat_tipos_nomina',       COUNT(*) FROM cat_tipos_nomina UNION ALL
-- SELECT 'cat_tipos_personal',     COUNT(*) FROM cat_tipos_personal UNION ALL
-- SELECT 'cat_universos',          COUNT(*) FROM cat_universos
-- ORDER BY 1;
--   -- esperado: puestos≈1772, sectores≈73, tipos_contratacion=7,
--   --           tipos_nomina=7, tipos_personal=11, universos=27
-- ============================================================
