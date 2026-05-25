-- ============================================================
-- sql/05-analisis/03-ranking-puestos-window.sql
--
-- Rankings de puestos por sueldo promedio usando funciones de
-- ventana. Demuestra el uso de RANK(), DENSE_RANK() y
-- ROW_NUMBER() y la diferencia entre ellos cuando hay empates.
--
-- Pregunta: ¿cuáles son los 15 puestos mejor pagados del padrón,
-- y cuántas personas ocupan cada uno?
-- ============================================================

WITH puestos_agregados AS (
    SELECT
        cp.nombre AS puesto,
        AVG(n.sueldo_bruto) AS sueldo_promedio,
        COUNT(*) AS n_ocupantes,
        MIN(n.sueldo_bruto) AS sueldo_min,
        MAX(n.sueldo_bruto) AS sueldo_max
    FROM nombramientos n
    JOIN cat_puestos cp ON cp.id = n.puesto_id
    GROUP BY cp.nombre
    HAVING COUNT(*) >= 1
)
SELECT
    ROW_NUMBER() OVER (ORDER BY sueldo_promedio DESC, puesto) AS row_n,
    RANK()       OVER (ORDER BY sueldo_promedio DESC)         AS rank_n,
    DENSE_RANK() OVER (ORDER BY sueldo_promedio DESC)         AS dense_rank_n,
    puesto,
    ROUND(sueldo_promedio::numeric, 2) AS sueldo_promedio,
    n_ocupantes,
    ROUND(sueldo_min::numeric, 2)      AS sueldo_min,
    ROUND(sueldo_max::numeric, 2)      AS sueldo_max
FROM puestos_agregados
ORDER BY sueldo_promedio DESC
LIMIT 15;
