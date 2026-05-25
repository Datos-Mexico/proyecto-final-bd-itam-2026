-- ============================================================
-- sql/05-analisis/04-percentiles-por-grupo.sql
--
-- Percentiles salariales por grupo etario y por sexo. Usa
-- `PERCENTILE_CONT WITHIN GROUP` para calcular cuartiles
-- y deciles dentro de cada grupo.
--
-- Pregunta: ¿cómo varía la distribución salarial entre rangos
-- de edad y entre sexos?
-- ============================================================

WITH grupo_etario AS (
    SELECT
        CASE
            WHEN p.edad < 26 THEN '1. 18-25'
            WHEN p.edad < 36 THEN '2. 26-35'
            WHEN p.edad < 46 THEN '3. 36-45'
            WHEN p.edad < 56 THEN '4. 46-55'
            ELSE '5. 56+'
        END AS rango_edad,
        sx.nombre AS sexo,
        n.sueldo_bruto
    FROM nombramientos n
    JOIN personas  p  ON p.id = n.persona_id
    JOIN cat_sexos sx ON sx.id = p.sexo_id
    WHERE p.edad IS NOT NULL AND n.sueldo_bruto IS NOT NULL
)
SELECT
    rango_edad,
    sexo,
    COUNT(*)                                                            AS n,
    ROUND(AVG(sueldo_bruto)::numeric, 2)                                AS sueldo_promedio,
    PERCENTILE_CONT(0.10) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2) AS p10,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2) AS mediana,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2) AS p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY sueldo_bruto)::numeric(12,2) AS p90
FROM grupo_etario
GROUP BY rango_edad, sexo
ORDER BY rango_edad, sexo;
