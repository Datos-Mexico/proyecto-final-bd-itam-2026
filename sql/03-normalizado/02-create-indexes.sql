-- ============================================================
-- sql/03-normalizado/02-create-indexes.sql
--
-- Índices que aceleran los joins frecuentes (catálogos) y los
-- predicados típicos de los endpoints (`/servidores/`,
-- `/sectores/`, `/analytics/`).
-- ============================================================

CREATE INDEX idx_nomb_persona_id          ON nombramientos(persona_id);
CREATE INDEX idx_nomb_sector_id           ON nombramientos(sector_id);
CREATE INDEX idx_nomb_puesto_id           ON nombramientos(puesto_id);
CREATE INDEX idx_nomb_sueldo_bruto        ON nombramientos(sueldo_bruto);
CREATE INDEX idx_nomb_tipo_contratacion   ON nombramientos(tipo_contratacion_id);
CREATE INDEX idx_nomb_tipo_personal       ON nombramientos(tipo_personal_id);
CREATE INDEX idx_nomb_universo_id         ON nombramientos(universo_id);
CREATE INDEX idx_nomb_nivel_salarial      ON nombramientos(nivel_salarial_id);

CREATE INDEX idx_personas_sexo_id         ON personas(sexo_id);
CREATE INDEX idx_personas_edad            ON personas(edad);
