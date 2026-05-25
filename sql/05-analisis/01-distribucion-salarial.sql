-- ============================================================
-- sql/05-analisis/01-distribucion-salarial.sql
--
-- Distribución salarial del padrón en cinco rangos de sueldo bruto,
-- con conteo y porcentaje del total. Replica la lógica del endpoint
-- `/api/v1/dashboard/stats` de la API académica.
-- ============================================================

WITH rangos AS (
    SELECT
        CASE
            WHEN sueldo_bruto < 5000  THEN '1. Menos de $5K'
            WHEN sueldo_bruto < 10000 THEN '2. $5K - $10K'
            WHEN sueldo_bruto < 20000 THEN '3. $10K - $20K'
            WHEN sueldo_bruto < 40000 THEN '4. $20K - $40K'
            ELSE '5. Más de $40K'
        END AS rango,
        sueldo_bruto
    FROM nombramientos
)
SELECT
    rango,
    COUNT(*) AS n,
    ROUND(AVG(sueldo_bruto)::numeric, 2) AS sueldo_promedio,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM rangos
GROUP BY rango
ORDER BY rango;
