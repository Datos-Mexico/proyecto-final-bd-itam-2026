-- ============================================================
-- 02-exploracion/05-distribucion-categorica.sql
--
-- Distribuciones de frecuencia para las variables categóricas
-- con baja cardinalidad. Detecta balanceos y posibles sesgos.
-- ============================================================

-- Distribución por sexo
SELECT
    sexo,
    COUNT(*) AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM servidores_publicos
GROUP BY sexo
ORDER BY n DESC;

-- Distribución por tipo de contratación
SELECT
    tc.nombre AS tipo_contratacion,
    COUNT(*)  AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM servidores_publicos sp
LEFT JOIN cat_tipos_contratacion tc ON tc.id = sp.tipo_contratacion_id
GROUP BY tc.nombre
ORDER BY n DESC;

-- Distribución por tipo de personal
SELECT
    tp.nombre AS tipo_personal,
    COUNT(*)  AS n,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM servidores_publicos sp
LEFT JOIN cat_tipos_personal tp ON tp.id = sp.tipo_personal_id
GROUP BY tp.nombre
ORDER BY n DESC;

-- Top 15 sectores por número de nombramientos
SELECT
    cs.nombre AS sector,
    COUNT(*) AS n
FROM servidores_publicos sp
LEFT JOIN cat_sectores cs ON cs.id = sp.sector_id
GROUP BY cs.nombre
ORDER BY n DESC
LIMIT 15;
