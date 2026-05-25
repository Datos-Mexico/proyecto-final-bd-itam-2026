-- ============================================================
-- 02-exploracion/03-estadisticas-numericas.sql
--
-- Estadísticas descriptivas de las columnas numéricas: edad,
-- sueldo_bruto, sueldo_neto. Cuartiles, media, desviación estándar.
-- ============================================================

SELECT
    'edad' AS columna,
    COUNT(*) FILTER (WHERE edad IS NOT NULL) AS n_no_null,
    ROUND(AVG(edad)::numeric, 2)                AS media,
    ROUND(STDDEV(edad)::numeric, 2)             AS desv_est,
    MIN(edad)                                   AS minimo,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY edad)::numeric(10,2) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY edad)::numeric(10,2) AS mediana,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY edad)::numeric(10,2) AS p75,
    MAX(edad)                                   AS maximo
FROM servidores_publicos
UNION ALL
SELECT
    'sueldo_bruto',
    COUNT(*) FILTER (WHERE sueldo_bruto IS NOT NULL),
    ROUND(AVG(sueldo_bruto)::numeric, 2),
    ROUND(STDDEV(sueldo_bruto)::numeric, 2),
    MIN(sueldo_bruto),
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2),
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2),
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2),
    MAX(sueldo_bruto)
FROM servidores_publicos
UNION ALL
SELECT
    'sueldo_neto',
    COUNT(*) FILTER (WHERE sueldo_neto IS NOT NULL),
    ROUND(AVG(sueldo_neto)::numeric, 2),
    ROUND(STDDEV(sueldo_neto)::numeric, 2),
    MIN(sueldo_neto),
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sueldo_neto)::numeric(12,2),
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY sueldo_neto)::numeric(12,2),
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sueldo_neto)::numeric(12,2),
    MAX(sueldo_neto)
FROM servidores_publicos
ORDER BY 1;
