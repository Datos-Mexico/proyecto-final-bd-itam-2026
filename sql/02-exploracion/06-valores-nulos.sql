-- ============================================================
-- 02-exploracion/06-valores-nulos.sql
--
-- Cuenta y proporción de valores NULL por columna. Permite
-- identificar columnas con cobertura parcial y guiar las
-- decisiones de NOT NULL en la capa 03 (normalización).
-- ============================================================

WITH conteos AS (
    SELECT
        COUNT(*)                                                    AS total,
        COUNT(*) FILTER (WHERE nombre               IS NULL)        AS n_nombre,
        COUNT(*) FILTER (WHERE apellido_1           IS NULL)        AS n_apellido_1,
        COUNT(*) FILTER (WHERE apellido_2           IS NULL)        AS n_apellido_2,
        COUNT(*) FILTER (WHERE sexo                 IS NULL)        AS n_sexo,
        COUNT(*) FILTER (WHERE edad                 IS NULL)        AS n_edad,
        COUNT(*) FILTER (WHERE puesto_id            IS NULL)        AS n_puesto,
        COUNT(*) FILTER (WHERE tipo_nomina_id       IS NULL)        AS n_tipo_nomina,
        COUNT(*) FILTER (WHERE tipo_contratacion_id IS NULL)        AS n_tipo_contratacion,
        COUNT(*) FILTER (WHERE tipo_personal_id     IS NULL)        AS n_tipo_personal,
        COUNT(*) FILTER (WHERE universo_id          IS NULL)        AS n_universo,
        COUNT(*) FILTER (WHERE sector_id            IS NULL)        AS n_sector,
        COUNT(*) FILTER (WHERE id_nivel_salarial    IS NULL)        AS n_nivel_salarial,
        COUNT(*) FILTER (WHERE sueldo_bruto         IS NULL)        AS n_sueldo_bruto,
        COUNT(*) FILTER (WHERE sueldo_neto          IS NULL)        AS n_sueldo_neto
    FROM servidores_publicos
)
SELECT 'nombre' AS columna,                         n_nombre           AS n_null, ROUND(100.0 * n_nombre/total, 4)           AS pct_null FROM conteos
UNION ALL SELECT 'apellido_1',                      n_apellido_1,         ROUND(100.0 * n_apellido_1/total, 4)       FROM conteos
UNION ALL SELECT 'apellido_2',                      n_apellido_2,         ROUND(100.0 * n_apellido_2/total, 4)       FROM conteos
UNION ALL SELECT 'sexo',                            n_sexo,               ROUND(100.0 * n_sexo/total, 4)             FROM conteos
UNION ALL SELECT 'edad',                            n_edad,               ROUND(100.0 * n_edad/total, 4)             FROM conteos
UNION ALL SELECT 'puesto_id',                       n_puesto,             ROUND(100.0 * n_puesto/total, 4)           FROM conteos
UNION ALL SELECT 'tipo_nomina_id',                  n_tipo_nomina,        ROUND(100.0 * n_tipo_nomina/total, 4)      FROM conteos
UNION ALL SELECT 'tipo_contratacion_id',            n_tipo_contratacion,  ROUND(100.0 * n_tipo_contratacion/total, 4) FROM conteos
UNION ALL SELECT 'tipo_personal_id',                n_tipo_personal,      ROUND(100.0 * n_tipo_personal/total, 4)    FROM conteos
UNION ALL SELECT 'universo_id',                     n_universo,           ROUND(100.0 * n_universo/total, 4)         FROM conteos
UNION ALL SELECT 'sector_id',                       n_sector,             ROUND(100.0 * n_sector/total, 4)           FROM conteos
UNION ALL SELECT 'id_nivel_salarial',               n_nivel_salarial,     ROUND(100.0 * n_nivel_salarial/total, 4)   FROM conteos
UNION ALL SELECT 'sueldo_bruto',                    n_sueldo_bruto,       ROUND(100.0 * n_sueldo_bruto/total, 4)     FROM conteos
UNION ALL SELECT 'sueldo_neto',                     n_sueldo_neto,        ROUND(100.0 * n_sueldo_neto/total, 4)      FROM conteos
ORDER BY pct_null DESC, columna;
