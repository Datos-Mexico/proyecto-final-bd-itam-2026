-- ============================================================
-- 02-exploracion/02-rango-fechas.sql
--
-- Rango temporal del Padrón. La fecha de ingreso es el único
-- atributo temporal del dataset; su distribución revela la
-- profundidad histórica del padrón vigente.
-- ============================================================

SELECT
    MIN(fecha_ingreso) AS fecha_minima,
    MAX(fecha_ingreso) AS fecha_maxima,
    MAX(fecha_ingreso) - MIN(fecha_ingreso) AS rango_dias,
    COUNT(*) FILTER (WHERE fecha_ingreso IS NULL) AS filas_sin_fecha_ingreso,
    ROUND(100.0 * COUNT(*) FILTER (WHERE fecha_ingreso IS NULL) / COUNT(*), 4) AS pct_sin_fecha
FROM servidores_publicos;

-- Distribución por década de ingreso
SELECT
    (EXTRACT(YEAR FROM fecha_ingreso)::int / 10) * 10 AS decada,
    COUNT(*) AS nombramientos
FROM servidores_publicos
WHERE fecha_ingreso IS NOT NULL
GROUP BY 1
ORDER BY 1;
