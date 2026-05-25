-- ============================================================
-- sql/05-analisis/02-brecha-genero-por-sector.sql
--
-- Brecha salarial por sexo en cada sector con al menos 100
-- nombramientos. La brecha se calcula como
-- (avgMale - avgFemale) / avgFemale * 100. Valores positivos indican
-- ventaja masculina; valores negativos, ventaja femenina.
--
-- Replica la lógica del campo `genderGapBySector` del endpoint
-- `/api/v1/dashboard/stats` y del endpoint `/analytics/sectores/ranking`.
-- ============================================================

WITH por_sector_sexo AS (
    SELECT
        s.id     AS sector_id,
        s.nombre AS sector,
        sx.nombre AS sexo,
        AVG(n.sueldo_bruto) AS avg_sueldo,
        COUNT(*) AS n
    FROM nombramientos n
    JOIN cat_sectores s ON s.id = n.sector_id
    JOIN personas     p ON p.id = n.persona_id
    JOIN cat_sexos    sx ON sx.id = p.sexo_id
    GROUP BY s.id, s.nombre, sx.nombre
),
pivoteado AS (
    SELECT
        sector,
        MAX(avg_sueldo) FILTER (WHERE sexo = 'MASCULINO') AS avg_masc,
        MAX(avg_sueldo) FILTER (WHERE sexo = 'FEMENINO')  AS avg_feme,
        SUM(n) AS total_nombramientos
    FROM por_sector_sexo
    GROUP BY sector
)
SELECT
    sector,
    ROUND(avg_masc::numeric, 2) AS avg_sueldo_masc,
    ROUND(avg_feme::numeric, 2) AS avg_sueldo_feme,
    ROUND(((avg_masc - avg_feme) / avg_feme * 100)::numeric, 2) AS brecha_pct,
    total_nombramientos
FROM pivoteado
WHERE avg_masc IS NOT NULL AND avg_feme IS NOT NULL
  AND total_nombramientos >= 100
ORDER BY brecha_pct DESC
LIMIT 20;
