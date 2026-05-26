-- ============================================================
-- sql/03-normalizado/01-create-tablas-normalizadas.sql
--
-- Crea los dos catálogos que faltaban en staging y las dos tablas
-- de datos normalizadas (`personas`, `nombramientos`). Diseño 4NF
-- que separa identidad (persona física) de relación laboral
-- (nombramiento).
-- ============================================================

BEGIN;

-- ------------------------------------------------------------
-- Catálogos faltantes en staging
-- ------------------------------------------------------------

CREATE TABLE cat_sexos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE cat_niveles_salariales (
    id    SERIAL PRIMARY KEY,
    clave INTEGER NOT NULL UNIQUE
);

-- ------------------------------------------------------------
-- personas — entidad identidad (datos estables del individuo)
-- ------------------------------------------------------------

CREATE TABLE personas (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(200) NOT NULL,
    apellido_1 VARCHAR(200) NOT NULL,
    apellido_2 VARCHAR(200),
    sexo_id    INTEGER REFERENCES cat_sexos(id),
    edad       INTEGER
);

-- ------------------------------------------------------------
-- nombramientos — entidad relación laboral (una persona puede
--   tener N nombramientos vigentes en distintos sectores).
-- ------------------------------------------------------------

CREATE TABLE nombramientos (
    id                   SERIAL PRIMARY KEY,
    persona_id           INTEGER NOT NULL REFERENCES personas(id),
    puesto_id            INTEGER REFERENCES cat_puestos(id),
    sector_id            INTEGER REFERENCES cat_sectores(id),
    tipo_nomina_id       INTEGER REFERENCES cat_tipos_nomina(id),
    tipo_contratacion_id INTEGER REFERENCES cat_tipos_contratacion(id),
    tipo_personal_id     INTEGER REFERENCES cat_tipos_personal(id),
    universo_id          INTEGER REFERENCES cat_universos(id),
    nivel_salarial_id    INTEGER REFERENCES cat_niveles_salariales(id),
    sueldo_bruto         NUMERIC(12,2),
    sueldo_neto          NUMERIC(12,2)
);

COMMIT;
